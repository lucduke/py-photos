import os
import hashlib
import sqlite3
from database import get_db_connection
from exif_utils import get_exif_data


def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def process_photos(directory):
    conn = get_db_connection()
    cursor = conn.cursor()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                file_hash = calculate_file_hash(file_path)
                file_size = os.path.getsize(file_path)
                exif_data = get_exif_data(file_path)

                try:
                    cursor.execute('''
                    INSERT INTO photos (file_path, file_hash, file_size, exif_data)
                    VALUES (?, ?, ?, ?)
                    ''', (file_path, file_hash, file_size, exif_data))
                except sqlite3.IntegrityError:
                    print(f"Doublon trouvé: {file_path}")

    conn.commit()
