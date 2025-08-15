#!/usr/bin/env python3
"""
Module contenant les modèles de données pour la reconnaissance de numéros de voitures
"""

import os
import base64
import time
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import logging

import anthropic
from dotenv import load_dotenv
from PIL import Image, ImageOps
import rawpy
import re
import tempfile


@dataclass
class Config:
    """Configuration du script"""
    api_key: str
    photos_folder: str
    output_file: str
    max_image_size: int = 1920  # Taille max en pixels
    convert_raw_size: int = 1024  # Taille pour conversion RAW
    converted_folder: str = "./converted_jpg"  # Dossier pour les JPG convertis
    supported_formats: List[str] = None
    raw_formats: List[str] = None
    delay_between_calls: float = 1.0  # Délai entre les appels API
    keep_converted: bool = True  # Garder les fichiers convertis

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
        if self.raw_formats is None:
            self.raw_formats = ['.cr3', '.cr2', '.arw', '.nef', '.orf', '.dng']


def load_config() -> Config:
    """
    Charge la configuration depuis les variables d'environnement
    
    Returns:
        Config: Configuration du script
    """
    # Chargement du fichier d'environnement (config.env ou .env)
    # Cherche d'abord config.env dans le répertoire parent du script
    script_dir = Path(__file__).parent
    config_env_path = script_dir.parent.parent / "config.env"
    if config_env_path.exists():
        load_dotenv(config_env_path)
    else:
        # Sinon cherche .env dans le répertoire parent
        dotenv_path = script_dir.parent / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
        else:
            # Cherche config.env dans le répertoire courant
            config_env_path = script_dir.parent / "config.env"
            if config_env_path.exists():
                load_dotenv(config_env_path)
            else:
                # Cherche .env dans le répertoire courant
                load_dotenv()
    
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError("CLAUDE_API_KEY non définie dans le fichier .env")
    
    photos_folder = script_dir.parent.parent / os.getenv('PHOTOS_FOLDER', './photos')
    output_file = script_dir.parent.parent / os.getenv('OUTPUT_FILE', 'car_numbers_results.txt')
    converted_folder = script_dir.parent.parent / os.getenv('CONVERTED_FOLDER', './converted_jpg')
    convert_raw_size = int(os.getenv('CONVERT_RAW_SIZE', '1024'))
    keep_converted = os.getenv('KEEP_CONVERTED', 'true').lower() == 'true'
    
    return Config(
        api_key=api_key,
        photos_folder=photos_folder,
        output_file=output_file,
        converted_folder=converted_folder,
        convert_raw_size=convert_raw_size,
        keep_converted=keep_converted
    )


class CarNumberRecognizer:
    """Classe principale pour la reconnaissance des numéros de voitures"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.results = []
        self.converted_files = []  # Liste des fichiers convertis
        
        # Création du dossier de conversion si nécessaire
        if config.keep_converted:
            Path(config.converted_folder).mkdir(exist_ok=True)
        
    def convert_raw_to_jpg(self, raw_path: Path) -> Optional[Path]:
        """
        Convertit un fichier RAW en JPEG
        
        Args:
            raw_path: Chemin vers le fichier RAW
            
        Returns:
            Path: Chemin vers le JPEG converti ou None en cas d'erreur
        """
        try:
            logging.info(f"Conversion RAW -> JPEG: {raw_path.name}")
            
            # Lecture du fichier RAW
            with rawpy.imread(str(raw_path)) as raw:
                # Traitement RAW avec paramètres optimisés
                rgb = raw.postprocess(
                    use_camera_wb=True,          # Balance des blancs de l'appareil
                    half_size=False,             # Pleine résolution
                    no_auto_bright=False,         # Correction auto luminosité
                    output_bps=8,                # 8 bits par canal
                    gamma=(2.222, 4.5),         # Gamma standard
                    bright=1.0,                  # Luminosité normale
                    highlight_mode=0,            # Gestion des hautes lumières
                    use_auto_wb=False           # Pas de balance auto
                )
            
            # Conversion en image PIL
            pil_image = Image.fromarray(rgb)
            
            # Redimensionnement à la taille demandée
            if max(pil_image.size) > self.config.convert_raw_size:
                ratio = self.config.convert_raw_size / max(pil_image.size)
                new_size = tuple(int(dim * ratio) for dim in pil_image.size)
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                logging.info(f"RAW redimensionné à {new_size}")
            
            # Nom du fichier de sortie
            if self.config.keep_converted:
                output_path = Path(self.config.converted_folder) / f"{raw_path.stem}.jpg"
            else:
                # Fichier temporaire
                temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', prefix='raw_conv_')
                os.close(temp_fd)
                output_path = Path(temp_path)
            
            # Sauvegarde en JPEG
            pil_image.save(
                output_path,
                format='JPEG',
                quality=90,
                optimize=True,
                exif=pil_image.getexif()  # Préservation EXIF si possible
            )
            
            self.converted_files.append(output_path)
            logging.info(f"✓ RAW converti: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Erreur conversion RAW {raw_path}: {e}")
            return None
    
    def load_and_resize_image(self, image_path: Path) -> Optional[bytes]:
        """
        Charge et redimensionne une image si nécessaire
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            bytes: Image encodée en base64 ou None en cas d'erreur
        """
        try:
            with Image.open(image_path) as img:
                # Correction automatique de l'orientation EXIF
                img = ImageOps.exif_transpose(img)
                
                # Redimensionner si nécessaire
                if max(img.size) > self.config.max_image_size:
                    ratio = self.config.max_image_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    logging.info(f"Image {image_path.name} redimensionnée à {new_size}")
                
                # Conversion en JPEG si nécessaire
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                # Sauvegarde temporaire et encodage
                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                return buffer.getvalue()
                
        except Exception as e:
            logging.error(f"Erreur lors du chargement de {image_path}: {e}")
            return None
    
    def analyze_image(self, image_path: Path) -> Optional[str]:
        """
        Analyse une image pour détecter le numéro de voiture
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            str: Numéro détecté ou None si échec
        """
        try:
            # Vérifier si c'est un fichier RAW
            if image_path.suffix.lower() in self.config.raw_formats:
                # Convertir le fichier RAW en JPEG
                converted_path = self.convert_raw_to_jpg(image_path)
                if converted_path is None:
                    logging.error(f"Échec de la conversion RAW pour {image_path}")
                    return None
                # Utiliser le fichier converti
                image_path = converted_path
            
            # Chargement de l'image
            image_data = self.load_and_resize_image(image_path)
            if image_data is None:
                return None
            
            # Encodage base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Appel à l'API Claude
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyse cette photo de course automobile et identifie UNIQUEMENT le numéro de la voiture de course. INSTRUCTIONS: Le numéro est affiché sur la carrosserie (portières, côté de la voiture, capot avant ou arrière, en dessous du pare-brise). Couleurs possibles: blanc sur un fond vert, rouge ou bleu. Ignore les numéros de sponsors. Réponds uniquement avec le numéro détecté, sans autre texte ni explication."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Extraction du numéro de la réponse
            response_text = response.content[0].text.strip()
            
            # Tentative d'extraction du numéro (recherche de patterns numériques)
            numbers = re.findall(r'\b\d+\b', response_text)
            
            if numbers:
                # Prendre le premier numéro trouvé (ou le plus long)
                detected_number = max(numbers, key=len) if len(numbers) > 1 else numbers[0]
                logging.info(f"Numéro détecté pour {image_path.name}: {detected_number}")
                return detected_number
            else:
                logging.warning(f"Aucun numéro détecté pour {image_path.name}. Réponse: {response_text}")
                return "NONE"
                
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de {image_path}: {e}")
            return None
    
    def get_image_files(self) -> List[Path]:
        """
        Récupère la liste des fichiers image dans le dossier (JPEG et RAW)
        
        Returns:
            List[Path]: Liste des chemins vers les images
        """
        photos_path = Path(self.config.photos_folder)
        if not photos_path.exists():
            raise FileNotFoundError(f"Le dossier {self.config.photos_folder} n'existe pas")
        
        image_files = []
        
        # Fichiers JPEG/PNG existants
        for ext in self.config.supported_formats:
            image_files.extend(photos_path.glob(f"*{ext}"))
            image_files.extend(photos_path.glob(f"*{ext.upper()}"))
        
        # Fichiers RAW
        for ext in self.config.raw_formats:
            image_files.extend(photos_path.glob(f"*{ext}"))
            image_files.extend(photos_path.glob(f"*{ext.upper()}"))
        
        image_files.sort()
        
        jpeg_count = len([f for f in image_files if f.suffix.lower() in self.config.supported_formats])
        raw_count = len([f for f in image_files if f.suffix.lower() in self.config.raw_formats])
        
        logging.info(f"Trouvé {len(image_files)} fichiers à traiter:")
        logging.info(f"  - {jpeg_count} fichiers JPEG/PNG")
        logging.info(f"  - {raw_count} fichiers RAW")
        
        return image_files
    
    def process_images(self):
        """Traite toutes les images du dossier"""
        image_files = self.get_image_files()
        
        if not image_files:
            logging.warning("Aucun fichier image trouvé")
            return
        
        # Générer un nom de fichier unique basé sur l'horodatage
        # from datetime import datetime
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_file_path = f"{self.config.output_file.rsplit('.', 1)[0]}_{timestamp}.{self.config.output_file.rsplit('.', 1)[1]}" if '.' in self.config.output_file else f"{self.config.output_file}_{timestamp}"
        
        # Stocker le nom du fichier généré dans l'objet pour l'affichage
        # self.output_file_path = output_file_path
        
        # Ouverture du fichier de résultats
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            f.write("filename;car_number\n")  # En-tête
            
            for i, image_path in enumerate(image_files, 1):
                logging.info(f"Traitement {i}/{len(image_files)}: {image_path.name}")
                
                # Analyse de l'image
                car_number = self.analyze_image(image_path)
                
                if car_number is not None:
                    # Écriture du résultat
                    f.write(f"{image_path.name};{car_number}\n")
                    f.flush()  # Force l'écriture immédiate
                    
                    self.results.append((image_path.name, car_number))
                    logging.info(f"✓ {image_path.name} -> {car_number}")
                else:
                    f.write(f"{image_path.name};ERROR\n")
                    f.flush()
                    logging.error(f"✗ Échec pour {image_path.name}")
                
                # Délai entre les appels pour respecter les limites d'API
                if i < len(image_files):
                    time.sleep(self.config.delay_between_calls)
    
    def cleanup_converted_files(self):
        """Nettoie les fichiers temporaires si nécessaire"""
        if not self.config.keep_converted:
            for file_path in self.converted_files:
                try:
                    if file_path.exists():
                        file_path.unlink()
                        logging.info(f"Fichier temporaire supprimé: {file_path}")
                except Exception as e:
                    logging.warning(f"Impossible de supprimer {file_path}: {e}")
    
    def generate_summary(self):
        """Génère un résumé des résultats"""
        total = len(self.results)
        successful = len([r for r in self.results if r[1] not in ['NONE', 'ERROR']])
        converted_count = len(self.converted_files)
        
        logging.info("\n=== RÉSUMÉ ===")
        logging.info(f"Images traitées: {total}")
        logging.info(f"Fichiers RAW convertis: {converted_count}")
        logging.info(f"Numéros détectés: {successful}")
        logging.info(f"Taux de succès: {successful/total*100:.1f}%" if total > 0 else "0%")
        
        if self.config.keep_converted and converted_count > 0:
            logging.info(f"Fichiers JPEG convertis sauvés dans: {self.config.converted_folder}")