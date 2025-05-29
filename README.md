# Photo Duplicate Finder

Une application Python pour identifier les doublons dans une bibliothèque de photos en utilisant l'empreinte numérique des fichiers et les métadonnées EXIF.

## Installation

1. Clonez le dépôt.
2. Installez les dépendances avec `pip install -r requirements.txt`.

## Utilisation

1. Modifiez le chemin du dossier dans `src/main.py`.
2. Exécutez l'application avec `python src/main.py`.

## Tests

Exécutez les tests avec `python -m unittest discover tests`.

## Structure du projet

```txt
/photo_duplicate_finder
│
├── /src
│   ├── __init__.py
│   ├── main.py          # Point d'entrée de l'application
│   ├── database.py      # Gestion de la base de données
│   ├── file_utils.py    # Fonctions utilitaires pour les fichiers
│   ├── exif_utils.py    # Fonctions utilitaires pour les métadonnées EXIF
│   └── duplicate_finder.py # Logique de recherche de doublons
│
├── /tests
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_file_utils.py
│   ├── test_exif_utils.py
│   └── test_duplicate_finder.py
│
├── requirements.txt     # Dépendances du projet
└── README.md            # Documentation du projet
```
