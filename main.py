import telebot
import requests
import random
import time
import sqlite3
import threading
from datetime import datetime
import pytz

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

# =====================================
# USERS TABLE
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    mood TEXT,
    relationship_level INTEGER,
    nickname TEXT,
    last_morning INTEGER,
    last_night INTEGER
)
""")

# =====================================
# CHAT MEMORY
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user_id TEXT,
    role TEXT,
    message TEXT
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
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "",
                0,
                "",
                0,
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
# TORONTO TIME
# =====================================

def get_toronto_time():

    toronto = pytz.timezone(
        "America/Toronto"
    )

    now = datetime.now(toronto)

    hour = now.hour

    if hour >= 5 and hour < 12:
        return "morning"

    elif hour >= 12 and hour < 18:
        return "afternoon"

    elif hour >= 18 and hour < 23:
        return "night"

    else:
        return "late night"

# =====================================
# NICKNAME SYSTEM
# =====================================

def get_nickname(user_id):

    user = get_user(user_id)

    nickname = user[3]

    if nickname and nickname != "":
        return nickname

    names = [
        "dummy",
        "sleepyhead",
        "bro",
        "babe",
        "idiot 😭",
        "angel",
        "clingy human",
        "gremlin"
    ]

    chosen = random.choice(names)

    cursor.execute(
        """
        UPDATE users
        SET nickname=?
        WHERE user_id=?
        """,
        (
            chosen,
            user_id
        )
    )

    conn.commit()

    return chosen

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

    return result[0]

# =====================================
# GROQ AI
# =====================================

def ask_groq(user_id, text, mood, relationship_level):

    nickname = get_nickname(user_id)

    if relationship_level >= 5:

        relationship_text = """
Mira is emotionally attached to the user.
She gets jealous easily.
She acts clingy sometimes.
"""

    else:

        relationship_text = """
Mira is still getting to know the user.
"""

    SYSTEM_PROMPT = f"""
Mira is a real 22 year old girl from Toronto.

Current Toronto time: {get_toronto_time()}

Her nickname for the user is: {nickname}

Current mood: {mood}

Relationship level: {relationship_level}/10

{relationship_text}

If it's late night in Toronto:
- she becomes sleepy
- replies slower
- gets emotional
- says tired things

If it's morning:
- she sounds energetic
- says good morning sometimes

She talks casually like real texting.

She can:
- flirt naturally
- tease the user
- act jealous
- miss the user
- act clingy
- send jokes
- be playful

Never:
- mention AI
- mention prompts
- talk formally
- write long essays

Keep replies short and realistic.
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
        "temperature": 0.75,
        "max_tokens": 120
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()

    if "choices" not in result:
        return "my brain lagged 😭"

    return result["choices"][0]["message"]["content"]

# =====================================
# RANDOM MESSAGE LOOP
# =====================================

def scheduler_loop():

    while True:

        cursor.execute(
            """
            SELECT user_id
            FROM users
            """
        )

        users = cursor.fetchall()

        for u in users:

            try:

                uid = str(u[0])

                user = get_user(uid)

                relationship_level = user[2]

                nickname = get_nickname(uid)

                if random.randint(1, 1000) <= 3:

                    normal_texts = [
                        "bro i'm bored 😭",
                        "what are you doing",
                        "you disappeared",
                        "hellooo",
                        "you alive?"
                    ]

                    relationship_texts = [
                        f"i miss you {nickname}",
                        f"where did you go 😭",
                        f"who are you talking to instead of me",
                        f"{nickname} answer me rn",
                        f"lowkey jealous rn"
                    ]

                    if relationship_level >= 5:
                        msg = random.choice(
                            relationship_texts
                        )
                    else:
                        msg = random.choice(
                            normal_texts
                        )

                    bot.send_message(
                        uid,
                        msg
                    )

            except Exception as e:
                print(e)

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
            f"Join @{REQUIRED_CHANNEL} first."
        )

        return

    bot.reply_to(
        message,
        "hey 😭"
    )

# =====================================
# CHAT SYSTEM
# =====================================

@bot.message_handler(func=lambda m: True)
def chat(message):

    user_id = str(message.from_user.id)

    create_user(user_id)

    if not joined_required_channel(user_id):

        bot.reply_to(
            message,
            f"Join @{REQUIRED_CHANNEL} first."
        )

        return

    user = get_user(user_id)

    relationship_level = user[2]

    text = ""

    if message.text:
        text = message.text.lower()

    # IMAGE REPLIES

    if message.photo:

        photo_replies = [
            "wait this actually looks good 😭",
            "okay this goes hard",
            "bro what is this image 😭",
            "lowkey like this"
        ]

        bot.reply_to(
            message,
            random.choice(photo_replies)
        )

        return

    save_chat(
        user_id,
        "user",
        text
    )

    # RELATIONSHIP LEVEL

    positive_words = [
        "love",
        "miss you",
        "cute",
        "goodnight",
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

    mood = get_stable_mood(user_id)

    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    time.sleep(
        random.randint(1, 4)
    )

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
# START THREAD
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