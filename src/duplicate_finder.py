from database import get_db_connection

def find_duplicates():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT file_path, COUNT(*) as count
    FROM photos
    GROUP BY file_hash
    HAVING count > 1
    ''')

    duplicates = cursor.fetchall()
    for duplicate in duplicates:
        print(f"Doublon trouvé: {duplicate[0]}")
