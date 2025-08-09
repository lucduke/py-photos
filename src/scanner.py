"""
Fonctionnalités pour scanner le système de fichiers à la recherche d'images.
"""

import logging
from pathlib import Path
from typing import Generator

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def find_jpeg_files(directory: Path) -> Generator[Path, None, None]:
    """
    Scanne un répertoire et ses sous-répertoires à la recherche de fichiers JPEG
    et les retourne via un générateur.

    Args:
        directory: Le chemin du répertoire à scanner.

    Yields:
        Le chemin d'un fichier JPEG trouvé.
    """
    logging.info(f"Début du scan dans le répertoire : {directory}")
    if not directory.is_dir():
        logging.error(f"Le chemin fourni n'est pas un répertoire valide : {directory}")
        return

    # Utilise rglob pour une recherche récursive et efficace
    for file_path in directory.rglob('*'):
        # On vérifie les extensions en minuscule
        if file_path.suffix.lower() in ['.jpg', '.jpeg']:
            yield file_path

    logging.info("Scan terminé.")