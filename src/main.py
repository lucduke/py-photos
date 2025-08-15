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
from py_photos.commands import run_car_recognition, run_move_photos
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
    
    return parser.parse_args()


def main():
    """Fonction principale"""
    # Parse les arguments de ligne de commande
    args = parse_args()
    # Pour le debug (a conserver)
    #args.car_recognition = True
    
    # Si aucun argument n'est fourni, affiche l'aide
    if not args.car_recognition and not args.move_photo:
        print("Veuillez spécifier une option : --car-recognition ou --move-photo")
        return
    
    try:
        # Chargement de la configuration
        config = load_config()
        logging.info("Configuration chargée avec succès")
        
        if args.car_recognition:
            # Exécution de la reconnaissance des numéros de voitures
            run_car_recognition(config)
        
        if args.move_photo:
            # Déplacement des photos selon les numéros de voiture
            run_move_photos(config)
        
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    main()

