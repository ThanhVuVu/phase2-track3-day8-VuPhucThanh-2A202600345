import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('checkpoints.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in checkpoints.db: {tables}")
        
        # Check checkpoints count
        if ('checkpoints',) in tables:
            cursor.execute("SELECT count(*) FROM checkpoints")
            count = cursor.fetchone()[0]
            print(f"Total checkpoints: {count}")
            
            # Show some thread_ids
            cursor.execute("SELECT DISTINCT thread_id FROM checkpoints LIMIT 5")
            threads = cursor.fetchall()
            print(f"Sample thread_ids: {threads}")
            
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_db()
