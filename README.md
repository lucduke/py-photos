# py-photos

Un package Python pour la reconnaissance de numéros de voitures dans des photos via l'API Claude d'Anthropic.

## Description

Ce projet permet d'automatiser la reconnaissance des numéros de voitures sur des photos de courses automobiles en utilisant l'API Claude d'Anthropic. Il supporte les formats d'image JPEG, PNG, WEBP ainsi que les formats RAW (CR3, CR2, ARW, NEF, ORF, DNG).

## Fonctionnalités

- Reconnaissance de numéros de voitures via l'API Claude
- Conversion des fichiers RAW en JPEG pour le traitement
- Déplacement des photos dans des sous-répertoires selon le numéro de voiture
- Support de plusieurs formats d'image
- Configuration via des variables d'environnement

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python src/main.py --car-recognition
python src/main.py --move-photo
```

## Configuration

Le projet utilise un fichier `.env` pour la configuration. Un exemple de fichier est fourni dans `config.env`.

## Structure du projet

```
py-photos/
├── src/
│   ├── main.py              # Point d'entrée principal
│   └── py_photos/           # Package principal
│       ├── __init__.py      # Fichier d'initialisation du package
│       ├── car_recognition.py # Module principal de reconnaissance
│       └── commands.py      # Commandes du programme
├── photos/                  # Dossier des photos à analyser
├── converted_jpg/           # Dossier des fichiers RAW convertis
├── car_numbers_results.txt  # Résultats de la reconnaissance
├── config.env               # Fichier de configuration
├── requirements.txt         # Dépendances du projet
└── setup.py                # Script d'installation
```

## Dépendances

- anthropic
- python-dotenv
- pillow
- rawpy
- imageio

## Licence

MIT
