from database import init_db, close_db
from duplicate_finder import find_duplicates
from file_utils import process_photos

def main():
    init_db()
    process_photos('votre_dossier')
    find_duplicates()
    close_db()

if __name__ == "__main__":
    main()
