"""
Couche d'accès aux données pour interagir avec la base de données SQLite.
"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from .models import Photo


class DatabaseRepository:
    """
    Gère toutes les opérations de base de données pour les photos.
    """

    def __init__(self, db_path: Path):
        """
        Initialise le repository et la connexion à la base de données.

        Args:
            db_path: Le chemin vers le fichier de base de données SQLite.
        """
        self.db_path = db_path
        self._conn = None

    def __enter__(self):
        """Permet d'utiliser le repository avec un 'with' statement."""
        self._conn = sqlite3.connect(self.db_path)
        # Ce 'row_factory' permet d'accéder aux résultats par nom de colonne
        self._conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme la connexion proprement."""
        if self._conn:
            self._conn.close()

    def _execute(self, query: str, params: tuple = ()):
        """Exécute une requête avec gestion des erreurs."""
        try:
            cursor = self._conn.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            logging.error(f"Erreur de base de données: {e}\nQuery: {query}")
            raise

    def setup_database(self):
        """
        Crée la table 'photos' si elle n'existe pas.
        """
        logging.info("Initialisation de la base de données...")
        query = """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            sha256_hash TEXT NOT NULL,
            capture_date TEXT,
            camera_model TEXT,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL
        );
        """
        self._execute(query)
        # Créer un index sur le hash pour accélérer la recherche de doublons
        index_query = "CREATE INDEX IF NOT EXISTS idx_sha256_hash ON photos (sha256_hash);"
        self._execute(index_query)
        self._conn.commit()
        logging.info("Base de données prête.")

    def add_photo(self, photo: Photo):
        """
        Ajoute une nouvelle photo à la base de données.
        """
        query = """
        INSERT INTO photos (path, filename, size_bytes, sha256_hash, capture_date, camera_model, width, height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            photo.path,
            photo.filename,
            photo.size_bytes,
            photo.sha256_hash,
            photo.capture_date.isoformat() if photo.capture_date else None,
            photo.camera_model,
            photo.dimensions[0],
            photo.dimensions[1]
        )
        self._execute(query, params)
        self._conn.commit()

    def get_photo_by_path(self, path: str) -> Optional[sqlite3.Row]:
        """Vérifie si une photo avec ce chemin existe déjà."""
        query = "SELECT id FROM photos WHERE path = ?;"
        cursor = self._execute(query, (path,))
        return cursor.fetchone()

    def find_exact_duplicates(self) -> List[Tuple[str, int, List[str]]]:
        """
        Trouve les groupes de photos ayant le même hash SHA-256.

        Returns:
            Une liste de tuples. Chaque tuple contient:
            (hash, nombre de doublons, liste des chemins des fichiers).
        """
        query = """
        SELECT sha256_hash, COUNT(id) as count, GROUP_CONCAT(path, ';') as paths
        FROM photos
        GROUP BY sha256_hash
        HAVING COUNT(id) > 1
        ORDER BY count DESC;
        """
        cursor = self._execute(query)
        results = []
        for row in cursor.fetchall():
            paths = row['paths'].split(';')
            results.append((row['sha256_hash'], row['count'], paths))
        return results