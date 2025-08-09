"""
Point d'entrée principal de l'application de gestion de photos.
Fournit une interface en ligne de commande (CLI) pour interagir avec l'outil.
"""

import argparse
import logging
import configparser
from pathlib import Path

from photo_manager import PhotoManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_db_path_from_config() -> Path:
    """Lit le fichier de configuration et retourne le chemin de la DB."""
    config = configparser.ConfigParser()
    # Le chemin est relatif au répertoire parent du répertoire 'src'
    config_path = Path(__file__).resolve().parent.parent / 'config.ini'
    
    if not config_path.exists():
        raise FileNotFoundError("Le fichier 'config.ini' est introuvable.")
        
    config.read(config_path)
    db_path_str = config.get('database', 'path', fallback='default_photo_library.db')
    return Path(db_path_str)


def main():
    """
    Fonction principale qui parse les arguments de la CLI et lance les actions.
    """
    parser = argparse.ArgumentParser(
        description="Outil d'analyse de photos pour trouver des doublons.",
        epilog="Exemple: python src/main.py scan /path/to/your/photos"
    )
    
    # Création de sous-commandes pour les différentes actions
    subparsers = parser.add_subparsers(dest='command', required=True, help='Action à effectuer')

    # Sous-commande 'scan'
    scan_parser = subparsers.add_parser('scan', help='Scanner un répertoire et ajouter les photos à la base de données.')
    scan_parser.add_argument(
        'directory',
        type=Path,
        help='Le répertoire contenant les photos à scanner.'
    )

    # Sous-commande 'find-duplicates'
    dups_parser = subparsers.add_parser('find-duplicates', help='Trouver et afficher les doublons exacts dans la bibliothèque.')

    args = parser.parse_args()

    # Initialisation du PhotoManager avec le chemin de la DB depuis la config
    try:
        db_path = get_db_path_from_config()
    except (FileNotFoundError, configparser.Error) as e:
        logging.error(f"Erreur de configuration : {e}")
        return

    manager = PhotoManager(db_path)

    if args.command == 'scan':
        if not args.directory.is_dir():
            logging.error(f"Le répertoire spécifié n'existe pas : {args.directory}")
            return
        manager.process_directory(args.directory)
        # Après un scan, on propose de chercher les doublons
        manager.find_and_report_duplicates()

    elif args.command == 'find-duplicates':
        manager.find_and_report_duplicates()


if __name__ == '__main__':
    main()