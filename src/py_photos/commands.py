#!/usr/bin/env python3
"""
Module pour gérer les différentes commandes du programme de reconnaissance de numéros de voitures
"""

import logging
from pathlib import Path
from .models import Config, CarNumberRecognizer


def run_car_recognition(config: Config) -> None:
    """
    Exécute la reconnaissance des numéros de voitures
    
    Args:
        config: Configuration du script
    """
    try:
        # Initialisation du recognizer
        recognizer = CarNumberRecognizer(config)
        
        # Traitement des images
        logging.info(f"Début du traitement des images dans: {config.photos_folder}")
        recognizer.process_images()
        
        # Génération du résumé
        recognizer.generate_summary()
        
        # Nettoyage des fichiers temporaires si nécessaire
        recognizer.cleanup_converted_files()
        
        # Utiliser le nom du fichier généré si disponible
        output_file_path = getattr(recognizer, 'output_file_path', config.output_file)
        logging.info(f"Résultats sauvegardés dans: {output_file_path}")
        
    except Exception as e:
        logging.error(f"Erreur lors de la reconnaissance des numéros de voitures: {e}")
        raise


def run_move_photos(config: Config) -> None:
    """
    Déplace les photos dans des sous-répertoires selon le numéro de voiture
    
    Args:
        config: Configuration du script
    """
    try:
        # Lecture du fichier de résultats
        results_file = Path(config.output_file)
        if not results_file.exists():
            logging.error(f"Le fichier de résultats {results_file} n'existe pas")
            return
        
        # Création d'un dictionnaire pour stocker les numéros de voiture et les fichiers associés
        car_files = {}
        
        with open(results_file, 'r', encoding='utf-8') as f:
            # Sauter l'en-tête
            next(f)
            
            for line in f:
                parts = line.strip().split(';')
                if len(parts) == 2:
                    filename, car_number = parts
                    if car_number not in ['ERROR', 'NONE']:
                        if car_number not in car_files:
                            car_files[car_number] = []
                        car_files[car_number].append(filename)
        
        # Déplacement des fichiers
        photos_path = Path(config.photos_folder)
        for car_number, files in car_files.items():
            # Création du sous-répertoire pour ce numéro de voiture
            car_folder = photos_path / f"car_{car_number}"
            car_folder.mkdir(exist_ok=True)
            
            # Déplacement des fichiers
            for filename in files:
                source_file = photos_path / filename
                destination_file = car_folder / filename
                
                if source_file.exists():
                    try:
                        source_file.rename(destination_file)
                        logging.info(f"Déplacé {filename} vers {car_folder}")
                    except Exception as e:
                        logging.error(f"Erreur lors du déplacement de {filename}: {e}")
                else:
                    logging.warning(f"Fichier {filename} non trouvé")
        
        logging.info("Déplacement des photos terminé")
        
    except Exception as e:
        logging.error(f"Erreur lors du déplacement des photos: {e}")
        raise