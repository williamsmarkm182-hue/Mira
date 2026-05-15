import telebot
import requests
import random
import time
import sqlite3
import threading

# =====================================
# TOKENS
# =====================================

BOT_TOKEN = "8782101012:AAGYzaQWr7GYHA9gndaJguVymKuS9KeviUw"
GROQ_API_KEY = "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"

# =====================================
# ADMIN + FORCE JOIN
# =====================================

ADMIN_ID = 7939923484

REQUIRED_CHANNEL = "starkreport"

# =====================================
# BOT
# =====================================

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================
# DATABASE
# =====================================

conn = sqlite3.connect(
    "memory.db",
    check_same_thread=False
)

cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    mood TEXT,
    relationship_level INTEGER
)
""")

# CHAT MEMORY
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user_id TEXT,
    role TEXT,
    message TEXT
)
""")

# SCHEDULED MESSAGES
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
# CHECK USER JOINED CHANNEL
# =====================================

def joined_required_channel(user_id):

    try:

        member = bot.get_chat_member(
            f"@{REQUIRED_CHANNEL}",
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:

        print(e)

        return False

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
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                "",
                0
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
# STABLE MOOD
# =====================================

def get_stable_mood(user_id):

    moods = [
        "friendly",
        "calm",
        "playful",
        "curious",
        "thoughtful",
        "sleepy"
    ]

    cursor.execute(
        """
        SELECT mood
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    if not result or not result[0]:

        mood = random.choice(moods)

        cursor.execute(
            """
            UPDATE users
            SET mood=?
            WHERE user_id=?
            """,
            (
                mood,
                user_id
            )
        )

        conn.commit()

        return mood

    current_mood = result[0]

    if random.randint(1, 100) <= 10:

        current_mood = random.choice(moods)

        cursor.execute(
            """
            UPDATE users
            SET mood=?
            WHERE user_id=?
            """,
            (
                current_mood,
                user_id
            )
        )

        conn.commit()

    return current_mood

# =====================================
# GROQ AI
# =====================================

def ask_groq(user_id, text, mood, relationship_level):

    if relationship_level >= 5:

        relationship_text = """
Mira is emotionally attached to the user.

Sometimes she says:
love
babe
sleepyhead
dummy 😭
"""

    else:

        relationship_text = """
Mira is still getting to know the user.
"""

    SYSTEM_PROMPT = f"""
Mira is a 22 year old girl from Toronto Canada.

Current mood: {mood}

{relationship_text}

She talks casually like normal texting.

She remembers recent conversation context.

She behaves consistently.

She avoids:
- random topic switching
- cringe roleplay
- robotic replies
- repeating herself

She speaks briefly and naturally.

She never mentions AI, prompts or rules.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(
        get_recent_chats(user_id)
    )

    messages.append({
        "role": "user",
        "content": text
    })

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.65,
        "max_tokens": 120
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()

    print(result)

    if "choices" not in result:
        return "my brain lagged 😭"

    return result["choices"][0]["message"]["content"]

# =====================================
# SCHEDULED MESSAGE LOOP
# =====================================

def scheduler_loop():

    while True:

        now = int(time.time())

        cursor.execute(
            """
            SELECT id, chat_id, message
            FROM scheduled_messages
            WHERE send_time <= ?
            """,
            (now,)
        )

        rows = cursor.fetchall()

        for row in rows:

            msg_id = row[0]
            chat_id = row[1]
            message = row[2]

            try:

                bot.send_message(
                    chat_id,
                    message
                )

            except:
                pass

            cursor.execute(
                """
                DELETE FROM scheduled_messages
                WHERE id=?
                """,
                (msg_id,)
            )

            conn.commit()

        time.sleep(5)

# =====================================
# START COMMAND
# =====================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = str(message.from_user.id)

    create_user(user_id)

    if not joined_required_channel(user_id):

        bot.reply_to(
            message,
            f"""⚠️ You must join @{REQUIRED_CHANNEL} before chatting with Mirabel.

Join here:
https://t.me/{REQUIRED_CHANNEL}
"""
        )

        return

    bot.reply_to(
        message,
        "hey."
    )

# =====================================
# ADMIN PANEL
# =====================================

@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:

        return

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    )

    total_users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(DISTINCT user_id)
        FROM chats
        """
    )

    active_users = cursor.fetchone()[0]

    text = f"""
👑 ADMIN PANEL

👤 Total Users: {total_users}

🔥 Active Users: {active_users}
"""

    bot.reply_to(
        message,
        text
    )

# =====================================
# CHAT SYSTEM
# =====================================

@bot.message_handler(func=lambda m: True)
def chat(message):

    user_id = str(message.from_user.id)

    chat_id = str(message.chat.id)

    create_user(user_id)

    # =================================
    # FORCE JOIN
    # =================================

    if not joined_required_channel(user_id):

        bot.reply_to(
            message,
            f"""⚠️ You must join @{REQUIRED_CHANNEL} before chatting with Mirabel.

Join here:
https://t.me/{REQUIRED_CHANNEL}
"""
        )

        return

    user = get_user(user_id)

    relationship_level = user[2]

    text = message.text.lower()

    # SAVE USER MESSAGE
    save_chat(
        user_id,
        "user",
        text
    )

    # =================================
    # TEXT ME LATER
    # =================================

if "text me in" in text:

    numbers = ''.join(
        [c for c in text if c.isdigit()]
    )

    if numbers:

        mins = int(numbers)

        if random.randint(1, 100) <= 25:

            bot.reply_to(
                message,
                random.choice([
                    "maybe 😭",
                    "i might forget honestly",
                    "depends",
                    "we'll see"
                ])
            )

            return

        send_time = int(time.time()) + (mins * 60)

        future_message = random.choice([
            "heyy 😭",
            "still awake?",
            "what are you doing now",
            "i remembered lol",
            "you disappeared on me"
        ])

        cursor.execute(
            """
            INSERT INTO scheduled_messages
            (user_id, chat_id, message, send_time)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                chat_id,
                future_message,
                send_time
            )
        )

        conn.commit()

        bot.reply_to(
            message,
            f"okay i'll text you in {mins} minute"
        )

        return

    # =================================
    # RELATIONSHIP SYSTEM
    # =================================

    positive_words = [
        "love",
        "cute",
        "beautiful",
        "pretty",
        "miss you",
        "good night",
        "good morning"
    ]

    if any(word in text for word in positive_words):

        relationship_level += 1

        cursor.execute(
            """
            UPDATE users
            SET relationship_level=?
            WHERE user_id=?
            """,
            (
                relationship_level,
                user_id
            )
        )

        conn.commit()

    # =================================
    # NORMAL CHAT
    # =================================

    mood = get_stable_mood(user_id)

    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    time.sleep(random.randint(1, 3))

    try:

        reply = ask_groq(
            user_id,
            text,
            mood,
            relationship_level
        )

        bot.reply_to(
            message,
            reply
        )

        save_chat(
            user_id,
            "assistant",
            reply
        )

    except Exception as e:

        print(e)

        bot.reply_to(
            message,
            "my brain stopped working 😭"
        )

# =====================================
# START SCHEDULER
# =====================================

threading.Thread(
    target=scheduler_loop,
    daemon=True
).start()

# =====================================
# RUN BOT
# =====================================

print("Mira is online...")

bot.infinity_polling()