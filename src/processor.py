"""
Fonctionnalités pour traiter une image : extraction EXIF et calcul de hash.
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS

from .models import Photo


def process_image(file_path: Path) -> Optional[Photo]:
    """
    Traite un fichier image pour en extraire les métadonnées et calculer un hash.

    Args:
        file_path: Le chemin vers le fichier image.

    Returns:
        Un objet Photo contenant les informations extraites, ou None si le fichier
        ne peut pas être traité.
    """
    try:
        with Image.open(file_path) as img:
            # 1. Extraire les données EXIF
            exif_data = img._getexif()
            capture_date = None
            camera_model = None
            if exif_data:
                # On décode les tags EXIF pour les rendre lisibles
                decoded_exif = {TAGS.get(key, key): val for key, val in exif_data.items()}
                
                # 'DateTimeOriginal' est le tag standard pour la date de prise de vue
                date_str = decoded_exif.get('DateTimeOriginal')
                if date_str:
                    # Le format est souvent 'YYYY:MM:DD HH:MM:SS'
                    capture_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                
                camera_model = decoded_exif.get('Model')

            # 2. Calculer le hash SHA-256 du fichier
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Lire le fichier par blocs pour ne pas surcharger la mémoire
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            # 3. Créer l'objet Photo
            photo = Photo(
                path=str(file_path.resolve()),
                filename=file_path.name,
                size_bytes=file_path.stat().st_size,
                sha256_hash=sha256_hash.hexdigest(),
                capture_date=capture_date,
                camera_model=camera_model,
                dimensions=img.size
            )
            return photo

    except Exception as e:
        logging.error(f"Impossible de traiter l'image {file_path}: {e}")
        return None