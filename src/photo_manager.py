"""
Le composant orchestrateur qui gère le processus de scan et d'analyse.
"""

import logging
from pathlib import Path

from .database import DatabaseRepository
from .processor import process_image
from .scanner import find_jpeg_files


class PhotoManager:
    """
    Orchestre le scan des répertoires, le traitement des images
    et la sauvegarde en base de données.
    """

    def __init__(self, db_path: Path):
        """
        Initialise le manager.

        Args:
            db_path: Chemin vers le fichier de la base de données SQLite.
        """
        self.db_path = db_path
        self.db_repo = DatabaseRepository(self.db_path)

    def process_directory(self, directory: Path):
        """
        Lance le processus complet de traitement pour un répertoire.

        Args:
            directory: Le répertoire à analyser.
        """
        logging.info(f"--- Début du traitement du répertoire {directory} ---")
        
        with self.db_repo as repo:
            # 1. Initialiser la base de données
            repo.setup_database()

            # 2. Scanner les fichiers
            image_paths = find_jpeg_files(directory)
            processed_count = 0
            skipped_count = 0

            for path in image_paths:
                # 3. Vérifier si la photo n'a pas déjà été traitée
                if repo.get_photo_by_path(str(path.resolve())):
                    logging.info(f"Photo déjà en base, ignorée : {path.name}")
                    skipped_count += 1
                    continue

                # 4. Traiter l'image
                logging.info(f"Traitement de l'image : {path.name}")
                photo = process_image(path)

                # 5. Sauvegarder en base
                if photo:
                    repo.add_photo(photo)
                    processed_count += 1
            
            logging.info(f"--- Traitement terminé ---")
            logging.info(f"{processed_count} nouvelle(s) photo(s) ajoutée(s).")
            logging.info(f"{skipped_count} photo(s) déjà existante(s) ignorée(s).")

    def find_and_report_duplicates(self):
        """
        Recherche les doublons et affiche un rapport.
        """
        logging.info("\n--- Recherche de doublons exacts (basée sur le hash) ---")
        with self.db_repo as repo:
            duplicates = repo.find_exact_duplicates()

            if not duplicates:
                logging.info("Aucun doublon exact trouvé.")
                return

            logging.warning(f"{len(duplicates)} groupe(s) de doublons trouvés.")
            for i, (sha_hash, count, paths) in enumerate(duplicates, 1):
                print(f"\nGroupe {i} (Hash: {sha_hash[:10]}..., {count} copies):")
                for path in paths:
                    print(f"  - {path}")