"""
Migration script to add llm_model column to users table.

This migration adds support for per-user LLM model selection.
"""
import sqlite3
import os

def migrate():
    """Add llm_model column to users table"""
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')

    print(f"Running migration on database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'llm_model' in columns:
            print("Migration skipped: llm_model column already exists")
            return

        print("Adding llm_model column to users table...")

        # Add column with default value
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN llm_model VARCHAR(100) DEFAULT 'openai-gpt-4o-mini'
        """)

        # Update existing users to have default model
        cursor.execute("""
            UPDATE users
            SET llm_model = 'openai-gpt-4o-mini'
            WHERE llm_model IS NULL
        """)

        conn.commit()
        print("Migration successful: llm_model column added")

        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM users WHERE llm_model = 'openai-gpt-4o-mini'")
        count = cursor.fetchone()[0]
        print(f"Updated {count} existing user(s) with default model")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
