"""
Database migration script to add new columns for task content
Run this once to update your existing database
"""
import sqlite3
import os

DATABASE_PATH = 'oleg.db'

def migrate_database():
    """Add new columns to existing database"""

    if not os.path.exists(DATABASE_PATH):
        print("Database does not exist yet. No migration needed.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Add new columns to activities table
        migrations = [
            "ALTER TABLE activities ADD COLUMN theory_content TEXT",
            "ALTER TABLE activities ADD COLUMN test_questions TEXT",
            "ALTER TABLE activities ADD COLUMN test_solutions TEXT",
            "ALTER TABLE activities ADD COLUMN content_generated BOOLEAN DEFAULT 0",
            "ALTER TABLE courses ADD COLUMN duration_weeks INTEGER DEFAULT 20",
            "ALTER TABLE courses ADD COLUMN start_date DATE"
        ]

        for migration in migrations:
            try:
                cursor.execute(migration)
                print(f"[OK] Executed: {migration}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"[SKIP] Column already exists: {migration}")
                else:
                    print(f"[ERROR] Error: {e}")

        conn.commit()
        print("\n[OK] Migration completed successfully!")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
