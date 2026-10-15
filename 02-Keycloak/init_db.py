"""
Database initialization and management module for Secure Notes.

Uses SQLite to persist notes created by authenticated users.
Each note is tied to a user's Keycloak subject identifier (sub) and username,
enabling strict user-level isolation and role-based administrative visibility.
"""

import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.
    Sets row_factory to sqlite3.Row so columns can be accessed by name like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed_samples: bool = True) -> None:
    """
    Initializes the SQLite database tables.
    Creates the 'notes' table if it does not already exist.
    Optionally seeds demonstration notes.
    """
    logger.info(f"Initializing database at: {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    logger.info("Table 'notes' created or verified successfully.")

    if seed_samples:
        # Check if table already has notes
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        count = cursor.fetchone()["count"]
        if count == 0:
            logger.info("Seeding demonstration notes for test accounts...")
            sample_notes = [
                (
                    "demo-user-id-001",
                    "testuser",
                    "Welcome to Secure Notes!",
                    "This note is private to testuser. Regular users can only see notes they created themselves.",
                ),
                (
                    "demo-user-id-001",
                    "testuser",
                    "Groceries and To-Do",
                    "1. Learn Keycloak OIDC\n2. Understand JWT roles\n3. Enjoy secure authentication!",
                ),
                (
                    "demo-admin-id-002",
                    "admin",
                    "System Maintenance Log",
                    "Keycloak realm notes-app configured with OAuth2 Authorization Code flow. RBAC verified.",
                ),
            ]
            cursor.executemany(
                """
                INSERT INTO notes (user_id, username, title, content)
                VALUES (?, ?, ?, ?)
                """,
                sample_notes,
            )
            conn.commit()
            logger.info(f"Seeded {len(sample_notes)} demonstration notes.")
        else:
            logger.info(f"Database already contains {count} note(s). Skipping seed.")

    conn.close()


def create_note(user_id: str, username: str, title: str, content: str) -> int:
    """
    Inserts a new note into the database.

    Args:
        user_id: Keycloak sub (UUID) of the user
        username: Keycloak preferred_username
        title: Note title
        content: Note content body

    Returns:
        The integer ID of the newly created note.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO notes (user_id, username, title, content)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, username, title, content),
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    logger.info(f"Created note #{note_id} for user '{username}' (sub={user_id})")
    return note_id


def get_notes_by_user(user_id: str) -> list:
    """
    Retrieves all notes created by a specific user.
    Enforces user isolation: regular users can only see their own notes.

    Args:
        user_id: Keycloak sub (UUID) of the requesting user

    Returns:
        List of sqlite3.Row dictionaries representing the user's notes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, username, title, content, created_at
        FROM notes
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,),
    )
    notes = cursor.fetchall()
    conn.close()
    return notes


def get_all_notes() -> list:
    """
    Retrieves all notes across all users.
    Only accessible by users with the 'admin' role.

    Returns:
        List of sqlite3.Row dictionaries representing all notes in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, username, title, content, created_at
        FROM notes
        ORDER BY created_at DESC, id DESC
        """
    )
    notes = cursor.fetchall()
    conn.close()
    return notes


def delete_note(note_id: int, user_id: str, is_admin: bool = False) -> bool:
    """
    Deletes a note by its ID.
    Enforces authorization:
    - Normal users can only delete their own notes (user_id must match).
    - Admins can delete any note.

    Args:
        note_id: Integer primary key of the note
        user_id: Keycloak sub (UUID) of the requesting user
        is_admin: True if user has the 'admin' role

    Returns:
        True if the note was deleted, False if note was not found or unauthorized.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if is_admin:
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    else:
        cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


if __name__ == "__main__":
    print("=" * 60)
    print("Initializing SQLite Database for Secure Notes Application...")
    print("=" * 60)
    init_db(seed_samples=True)
    print(f"Database setup complete! SQLite file: {DB_PATH}")
