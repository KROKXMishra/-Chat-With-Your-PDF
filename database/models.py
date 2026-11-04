def get_columns(conn, table_name):
    rows = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return {row["name"] for row in rows}


def create_tables(conn):

    # 1. Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 2. Conversations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pdf_name TEXT NOT NULL,
            pdf_path TEXT,
            vectorstore_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # 3. Migrate older conversations table
    columns = get_columns(conn, "conversations")

    if "user_id" not in columns:
        conn.execute("""
            ALTER TABLE conversations
            ADD COLUMN user_id INTEGER
            REFERENCES users(id)
            ON DELETE CASCADE
        """)

    if "pdf_path" not in columns:
        conn.execute("""
            ALTER TABLE conversations
            ADD COLUMN pdf_path TEXT
        """)

    if "vectorstore_path" not in columns:
        conn.execute("""
            ALTER TABLE conversations
            ADD COLUMN vectorstore_path TEXT
        """)

    # Check essential conversation columns
    columns = get_columns(conn, "conversations")

    required_conversation_columns = {
        "id",
        "pdf_name",
        "created_at",
        "user_id",
        "pdf_path",
        "vectorstore_path"
    }

    missing = required_conversation_columns - columns

    if missing:
        raise RuntimeError(
            f"Conversations table is missing columns: {missing}"
        )

    # 4. Messages table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE
        )
    """)

    # 5. Migrate older messages table
    columns = get_columns(conn, "messages")

    required_message_columns = {
        "conversation_id",
        "role",
        "content"
    }

    missing = required_message_columns - columns

    if missing:
        raise RuntimeError(
            f"Messages table is missing essential columns: {missing}"
        )

    # Add timestamp if an older table does not have it
    if "timestamp" not in columns:

        conn.execute("""
            ALTER TABLE messages
            ADD COLUMN timestamp TEXT NOT NULL DEFAULT ''
        """)

        conn.execute("""
            UPDATE messages
            SET timestamp = CURRENT_TIMESTAMP
            WHERE timestamp = ''
        """)

    # 6. Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_user
        ON conversations(user_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_conversation
        ON messages(conversation_id)
    """)