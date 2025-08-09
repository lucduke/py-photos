"""
Définit les modèles de données pour l'application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class Photo:
    """
    Représente une photo et ses métadonnées extraites.
    """
    path: str
    filename: str
    size_bytes: int
    sha256_hash: str
    capture_date: Optional[datetime]
    camera_model: Optional[str]
    dimensions: Tuple[int, int]