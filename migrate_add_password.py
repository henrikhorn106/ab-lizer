"""
Database Migration Script: Add password_hash column to users table

This script adds the password_hash field to the users table for authentication.
Run this once to update your existing database.

Usage:
    python migrate_add_password.py
"""

import os
import sys
from sqlalchemy import text

# Add the parent directory to the path so we can import from data
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db


def migrate_database():
    """Add password_hash column to users table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if 'password_hash' in columns:
                print("✓ password_hash column already exists in users table")
                return True

            # Add password_hash column
            print("Adding password_hash column to users table...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"
            ))
            db.session.commit()
            print("✓ Successfully added password_hash column")

            # Make email unique
            print("\nNote: To make email unique, you'll need to recreate the table or use a proper migration tool like Alembic")
            print("For now, the application will work with non-unique emails, but registration will check for duplicates")

            return True

        except Exception as e:
            print(f"✗ Error during migration: {str(e)}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Add Authentication Support")
    print("=" * 60)
    print()

    success = migrate_database()

    print()
    print("=" * 60)
    if success:
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("1. Existing users will need passwords set manually")
        print("2. New users can register with the /register page")
        print("3. Users can now login at /login")
    else:
        print("MIGRATION FAILED")
        print("Please check the error message above")
    print("=" * 60)