# Architecture de l'Application de Détection de Doublons de Photos

Ce document décrit l'architecture logicielle pour l'application de recherche, d'analyse et de détection de doublons de photos.

## 1. Objectifs

L'application vise à :

1. **Scanner** une arborescence de répertoires pour trouver des images JPEG.
2. **Extraire** les métadonnées EXIF de chaque image.
3. **Calculer** une empreinte unique (hash SHA-256) pour identifier les doublons exacts.
4. **Stocker** les informations collectées (chemin, EXIF, hash, taille) dans une base de données SQLite.
5. **Analyser** la base de données pour identifier les doublons exacts et potentiels.

## 2. Diagramme d'Architecture

L'application suit une architecture en couches pour séparer les responsabilités, améliorer la testabilité et la maintenabilité.

```mermaid
graph TD
    subgraph "Interface Utilisateur"
        A[CLI (main.py)]
    end

    subgraph "Couche Logique (Cœur de l'application)"
        B[PhotoManager (photo_manager.py)]
    end

    subgraph "Couche d'Accès aux Données"
        C[DatabaseRepository (database.py)]
        D[PhotoModel (models.py)]
    end

    subgraph "Couche Utilitaires"
        E[FileScanner (scanner.py)]
        F[ImageProcessor (processor.py)]
    end

    A -- Lance le processus --> B
    B -- Utilise --> E
    B -- Utilise --> F
    B -- Utilise --> C
    F -- Crée --> D
    C -- Gère --> D
```

## 3. Description des Composants

### `models.py` (Modèle de Données)

- **Rôle** : Définit la structure de l'objet `Photo` à l'aide d'une `dataclass` Python pour une représentation claire et typée des données.
- **Structure** :

  ```python
  @dataclass
  class Photo:
      path: str
      filename: str
      size_bytes: int
      sha256_hash: str
      capture_date: Optional[datetime]
      camera_model: Optional[str]
      dimensions: Tuple[int, int]
  ```

### `scanner.py` (Scanner de Fichiers)

- **Rôle** : Parcourt récursivement un répertoire pour trouver tous les fichiers avec les extensions `.jpg` ou `.jpeg`.
- **Implémentation** : Utilise `pathlib.Path.rglob` et un générateur (`yield`) pour une gestion mémoire efficace, même avec un grand nombre de fichiers.

### `processor.py` (Processeur d'Image)

- **Rôle** : Isole toute la logique de traitement pour un seul fichier image.
- **Fonctionnalités** :
  - **Extraction EXIF** : Lit les métadonnées pertinentes en utilisant la bibliothèque `Pillow`.
    - **Calcul du Hash** : Calcule le hash SHA-256 du contenu binaire du fichier avec `hashlib` pour une identification fiable des doublons exacts.

### `database.py` (Référentiel de Base de Données)

- **Rôle** : Centralise toutes les opérations de base de données (CRUD) en appliquant le *Repository Pattern*. C'est le seul module autorisé à communiquer avec la base de données SQLite.
- **Méthodes clés** : `setup_database()`, `add_photo()`, `get_photo_by_hash()`, `find_exact_duplicates()`, `find_potential_duplicates()`.

### `photo_manager.py` (Orchestrateur)

- **Rôle** : Coordonne l'ensemble du flux de travail de l'application.
- **Logique** :
    1. Initialise le `DatabaseRepository`.
    2. Utilise le `FileScanner` pour obtenir les chemins des images.
    3. Pour chaque chemin, invoque l'`ImageProcessor`.
    4. Sauvegarde l'objet `Photo` résultant via le `DatabaseRepository`.
    5. Lance les analyses de détection de doublons.

### `main.py` (Point d'Entrée / CLI)

- **Rôle** : Fournit l'interface en ligne de commande (CLI) pour l'utilisateur.
- **Implémentation** : Utilise le module `argparse` pour gérer les arguments de la ligne de commande, comme le chemin du répertoire à analyser.

## 4. Choix Techniques et Justifications

- **Langage** : Python 3.8+
- **Base de données** : SQLite (via le module `sqlite3`) pour sa simplicité et son intégration sans serveur.
- **Bibliothèques clés** :
  - `Pillow`: Pour le traitement d'images et l'extraction EXIF.
  - `pathlib`: Pour une manipulation moderne et orientée objet des chemins de fichiers.
- **Principes** : L'architecture est conçue autour des principes SOLID pour garantir un code découplé, testable et maintenable.

## 5. Évolutions Possibles

- **Détection de similarité** : Intégration d'algorithmes de *perceptual hashing* (pHash) avec la bibliothèque `imagehash` pour trouver des images quasi-identiques (recadrées, redimensionnées).
- **Rapports** : Création d'un module `reporting.py` pour générer des rapports sur les doublons (CSV, HTML).
- **Interface Graphique** : Développement d'une interface utilisateur graphique (GUI) avec Tkinter, PyQt ou une interface web.
