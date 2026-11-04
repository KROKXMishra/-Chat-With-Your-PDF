import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DB_PATH = BASE_DIR / "chat_history.db"


# Create and return database connection
def get_connection():

    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=30
    )

    # Return dictionary-like rows
    conn.row_factory = sqlite3.Row

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# Initialize database
def init_db():

    from database.models import create_tables

    conn = get_connection()

    try:

        # Begin transaction
        conn.execute("BEGIN")

        # Create tables and run migrations
        create_tables(conn)

        # Commit changes
        conn.commit()

    except Exception:

        # Roll back if anything fails
        conn.rollback()

        raise

    finally:

        # Always close connection
        conn.close()