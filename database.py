import sqlite3

# =====================================
# CONNECT DATABASE
# =====================================

conn = sqlite3.connect(
    "memory.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =====================================
# USERS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    mood TEXT,
    relationship_level INTEGER,
    nickname TEXT
)
""")

# =====================================
# CHATS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user_id TEXT,
    role TEXT,
    message TEXT
)
""")

# =====================================
# MEMORIES TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
    user_id TEXT,
    memory TEXT
)
""")

# =====================================
# SCHEDULED MESSAGES TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    chat_id TEXT,
    message TEXT,
    send_time INTEGER
)
""")

conn.commit()

# =====================================
# CREATE USER
# =====================================

def create_user(user_id):

    cursor.execute(
        """
        SELECT * FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:

        cursor.execute(
            """
            INSERT INTO users
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                "",
                0,
                ""
            )
        )

        conn.commit()

# =====================================
# GET USER
# =====================================

def get_user(user_id):

    cursor.execute(
        """
        SELECT * FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cursor.fetchone()

# =====================================
# SAVE CHAT
# =====================================

def save_chat(user_id, role, message):

    cursor.execute(
        """
        INSERT INTO chats
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            role,
            message
        )
    )

    conn.commit()

# =====================================
# GET RECENT CHATS
# =====================================

def get_recent_chats(user_id):

    cursor.execute(
        """
        SELECT role, message
        FROM chats
        WHERE user_id=?
        ORDER BY rowid DESC
        LIMIT 12
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    rows.reverse()

    messages = []

    for role, msg in rows:

        messages.append({
            "role": role,
            "content": msg
        })

    return messages

# =====================================
# SAVE MEMORY
# =====================================

def save_memory(user_id, memory):

    cursor.execute(
        """
        INSERT INTO memories
        VALUES (?, ?)
        """,
        (
            user_id,
            memory
        )
    )

    conn.commit()

# =====================================
# GET MEMORIES
# =====================================

def get_memories(user_id):

    cursor.execute(
        """
        SELECT memory
        FROM memories
        WHERE user_id=?
        LIMIT 10
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    return [row[0] for row in rows]

# =====================================
# SAVE SCHEDULED MESSAGE
# =====================================

def save_scheduled_message(
    user_id,
    chat_id,
    message,
    send_time
):

    cursor.execute(
        """
        INSERT INTO scheduled_messages
        (user_id, chat_id, message, send_time)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            chat_id,
            message,
            send_time
        )
    )

    conn.commit()

# =====================================
# GET DUE MESSAGES
# =====================================

def get_due_messages(now):

    cursor.execute(
        """
        SELECT id, chat_id, message
        FROM scheduled_messages
        WHERE send_time <= ?
        """,
        (now,)
    )

    return cursor.fetchall()

# =====================================
# DELETE SCHEDULED MESSAGE
# =====================================

def delete_scheduled_message(msg_id):

    cursor.execute(
        """
        DELETE FROM scheduled_messages
        WHERE id=?
        """,
        (msg_id,)
    )

    conn.commit()