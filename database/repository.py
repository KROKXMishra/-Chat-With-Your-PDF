from datetime import datetime, timezone

from database.connection import get_connection

# Generate current UTC timestamp
def current_time():

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================
# USER OPERATIONS
# =========================

# Create a new user
def create_user(name, email, password_hash):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            INSERT INTO users (
                name,
                email,
                password,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                current_time()
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


# Find user using email
def get_user_by_email(email):

    conn = get_connection()

    try:

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                password,
                created_at
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        return user

    finally:
        conn.close()


# Find user using ID
def get_user_by_id(user_id):

    conn = get_connection()

    try:

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        return user

    finally:
        conn.close()


# =========================
# CONVERSATION OPERATIONS
# =========================

# Create a new conversation
def create_conversation(user_id, pdf_name):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            INSERT INTO conversations (
                user_id,
                pdf_name,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                pdf_name,
                current_time()
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


# Get all conversations of a user
def get_all_chats(user_id):

    conn = get_connection()

    try:

        chats = conn.execute(
            """
            SELECT
                id,
                pdf_name,
                created_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

        return chats

    finally:
        conn.close()


# Get one conversation after verifying ownership
def get_conversation(chat_id, user_id):

    conn = get_connection()

    try:

        chat = conn.execute(
            """
            SELECT
                id,
                user_id,
                pdf_name,
                pdf_path,
                vectorstore_path,
                created_at
            FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (chat_id, user_id)
        ).fetchone()

        return chat

    finally:
        conn.close()


# Update original PDF path
def update_conversation_pdf_path(
    chat_id,
    user_id,
    pdf_path
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            UPDATE conversations
            SET pdf_path = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                pdf_path,
                chat_id,
                user_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# Update FAISS index path
def update_vectorstore_path(
    chat_id,
    user_id,
    vectorstore_path
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            UPDATE conversations
            SET vectorstore_path = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                vectorstore_path,
                chat_id,
                user_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# Count conversations referencing the same PDF
def count_pdf_references(pdf_path, user_id):

    if not pdf_path:
        return 0

    conn = get_connection()

    try:

        result = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM conversations
            WHERE user_id = ? AND pdf_path = ?
            """,
            (
                user_id,
                pdf_path
            )
        ).fetchone()

        return result["total"]

    finally:
        conn.close()


# Delete one conversation
def delete_chat(chat_id, user_id):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            DELETE FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (
                chat_id,
                user_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# Delete all conversations of a user
def delete_all_chats(user_id):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            DELETE FROM conversations
            WHERE user_id = ?
            """,
            (user_id,)
        )

        conn.commit()

        return cursor.rowcount

    finally:
        conn.close()


# =========================
# MESSAGE OPERATIONS
# =========================

# Save a message
def save_message(
    chat_id,
    user_id,
    role,
    content
):

    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role.")

    if not isinstance(content, str):
        raise ValueError("Message content must be text.")

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content,
                timestamp
            )
            SELECT ?, ?, ?, ?
            WHERE EXISTS (
                SELECT 1
                FROM conversations
                WHERE id = ? AND user_id = ?
            )
            """,
            (
                chat_id,
                role,
                content,
                current_time(),
                chat_id,
                user_id
            )
        )

        conn.commit()

        if cursor.rowcount == 0:

            raise ValueError(
                "Conversation not found or access denied."
            )

    finally:
        conn.close()


# Retrieve messages of one conversation
def get_messages(chat_id, user_id):

    conn = get_connection()

    try:

        messages = conn.execute(
            """
            SELECT
                m.role,
                m.content,
                m.timestamp
            FROM messages AS m
            INNER JOIN conversations AS c
                ON m.conversation_id = c.id
            WHERE c.id = ? AND c.user_id = ?
            ORDER BY m.rowid ASC
            """,
            (
                chat_id,
                user_id
            )
        ).fetchall()

        return messages

    finally:
        conn.close()