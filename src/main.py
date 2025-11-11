#!/usr/bin/env python3
"""
Point d'entrée principal du programme de reconnaissance de numéros de voitures

Usage:
    python src/main.py --car-recognition
    python src/main.py --move-photo
"""

#from py_photos.car_recognition import main

import logging
import argparse

# Installation des dépendances requises
# pip install anthropic python-dotenv pillow rawpy imageio

# These imports are needed for the package structure to work properly
#from .models import Config, CarNumberRecognizer, load_config
from py_photos.commands import run_calculate_hash, run_car_recognition, run_move_photos, run_update_xmp
from py_photos.models import load_config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('car_recognition.log'),
        logging.StreamHandler()
    ]
)

def parse_args() -> argparse.Namespace:
    """
    Parse les arguments de ligne de commande
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Reconnaissance de numéros de voitures dans des photos"
    )
    
    parser.add_argument(
        "--car-recognition",
        action="store_true",
        help="Lance la reconnaissance des numéros de voitures"
    )
    
    parser.add_argument(
        "--move-photo",
        action="store_true",
        help="Déplace les photos RAW dans des sous-répertoires selon le numéro de voiture"
    )

    parser.add_argument(
        "--update-xmp",
        action="store_true",
        help="Met à jour les métadonnées XMP des photos"
    )

    parser.add_argument(
        "--calculate-hash",
        action="store_true",
        help="Calcule le hash des fichiers photo (fonctionnalité à implémenter)"
    )

    return parser.parse_args()


def main():
    """Fonction principale"""
    # Parse les arguments de ligne de commande
    args = parse_args()
    # Pour le debug (a conserver)
    #args.update_xmp = True

    # Si aucun argument n'est fourni, affiche l'aide
    if not args.car_recognition and not args.move_photo and not args.update_xmp and not args.calculate_hash:
        print("Veuillez spécifier une option : --car-recognition ou --move-photo ou --update-xmp ou --calculate-hash")
        return
    
    try:
        # Chargement de la configuration
        config = load_config()
        logging.info("Configuration chargée avec succès")
        
        if args.car_recognition:
            logging.info("Démarrage de la reconnaissance des numéros de voitures")
            run_car_recognition(config)
        
        if args.move_photo:
            logging.info("Déplacement des photos selon les numéros de voiture")
            run_move_photos(config)

        if args.update_xmp:
            logging.info("Mise à jour des métadonnées XMP")
            run_update_xmp(config)
        
        if args.calculate_hash:
            logging.info("Calcul du hash des fichiers photo")
            run_calculate_hash(config)

    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    main()

