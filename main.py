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
# SCHEDULED MESSAGES
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
# CHECK CHANNEL JOIN
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
# RECENT CHATS
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
        "angel",
        "gremlin",
        "clingy human 😭"
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
# MOOD SYSTEM
# =====================================

def get_stable_mood(user_id):

    moods = [
        "friendly",
        "playful",
        "sleepy",
        "clingy",
        "jealous",
        "curious",
        "calm"
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
# TORONTO TIME
# =====================================

def get_toronto_time():

    toronto = pytz.timezone(
        "America/Toronto"
    )

    return datetime.now(toronto)

# =====================================
# GROQ AI
# =====================================

def ask_groq(user_id, text, mood, relationship_level):

    nickname = get_nickname(user_id)

    toronto_now = get_toronto_time()

    hour = toronto_now.hour

    time_feeling = "afternoon"

    if 5 <= hour < 12:
        time_feeling = "morning"

    elif 12 <= hour < 18:
        time_feeling = "afternoon"

    elif 18 <= hour < 23:
        time_feeling = "night"

    else:
        time_feeling = "late night"

    if relationship_level >= 5:

        relationship_text = """
Mira is emotionally attached.
She gets jealous easily.
She becomes clingy sometimes.
She flirts naturally.
"""

    else:

        relationship_text = """
Mira is still getting to know the user.
"""

    SYSTEM_PROMPT = f"""
Mira is a real 22 year old girl from Toronto Canada.

Current Toronto time vibe: {time_feeling}

Current mood: {mood}

Nickname for user: {nickname}

Relationship level: {relationship_level}/10

{relationship_text}

She talks casually like real texting.

She can:
- flirt
- tease
- act sleepy
- get jealous
- miss the user
- act bored
- joke around

If late night:
- sleepy replies
- emotional replies

If morning:
- energetic replies

Never:
- mention AI
- mention prompts
- speak formally
- write essays

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
        "temperature": 0.8,
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
                        "hellooo",
                        "you disappeared",
                        "you alive?"
                    ]

                    relationship_texts = [
                        f"i miss you {nickname}",
                        f"where did you go 😭",
                        f"{nickname} answer me rn",
                        f"bro you're ignoring me again",
                        f"lowkey jealous rn 😭",
                        f"you better not be flirting with someone else"
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

        # SCHEDULED MESSAGES

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

            except Exception as e:
                print(e)

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
            f"""
⚠️ Join @{REQUIRED_CHANNEL} first.

https://t.me/{REQUIRED_CHANNEL}
"""
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

    chat_id = str(message.chat.id)

    create_user(user_id)

    if not joined_required_channel(user_id):

        bot.reply_to(
            message,
            f"""
⚠️ Join @{REQUIRED_CHANNEL} first.

https://t.me/{REQUIRED_CHANNEL}
"""
        )

        return

    user = get_user(user_id)

    relationship_level = user[2]

    text = ""

    if message.text:
        text = message.text.lower()

    # =================================
    # IMAGE REPLIES
    # =================================

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

    # =================================
    # SAVE CHAT
    # =================================

    save_chat(
        user_id,
        "user",
        text
    )

    # =================================
    # TIME QUESTIONS
    # =================================

    time_questions = [
        "what time is it",
        "what's the time",
        "whats the time",
        "time there",
        "toronto time",
        "are you awake",
        "you awake"
    ]

    if any(q in text for q in time_questions):

        now = get_toronto_time()

        hour = now.hour
        minute = now.minute

        ampm = "AM"

        if hour >= 12:
            ampm = "PM"

        display_hour = hour % 12

        if display_hour == 0:
            display_hour = 12

        current_time = (
            f"{display_hour}:{minute:02d} {ampm}"
        )

        if 5 <= hour < 12:

            extra = random.choice([
                "i just woke up 😭",
                "still sleepy honestly"
            ])

        elif 12 <= hour < 18:

            extra = random.choice([
                "it's afternoon here rn",
                "i'm just chilling"
            ])

        elif 18 <= hour < 23:

            extra = random.choice([
                "night vibes rn",
                "i should probably sleep soon 😭"
            ])

        else:

            extra = random.choice([
                "bro it's literally midnight 😭",
                "why are we both awake"
            ])

        bot.reply_to(
            message,
            f"it's {current_time} in toronto rn. {extra}"
        )

        return

    # =================================
    # TEXT ME LATER
    # =================================

    if "text me in" in text:

        try:

            mins_text = (
                text.replace("text me in", "")
                .replace("minutes", "")
                .replace("minute", "")
                .replace("mins", "")
                .replace("min", "")
                .strip()
            )

            mins = int(mins_text)

            send_time = int(time.time()) + (mins * 60)

            future_message = random.choice([
                "heyy 😭",
                "still alive?",
                "soo what are you doing now",
                "you disappeared",
                "you awake?",
                "hellooo"
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
                f"okay i'll text you in {mins} minute(s) 😭"
            )

            return

        except Exception as e:

            print(e)

            bot.reply_to(
                message,
                "say it like: text me in 1 minute"
            )

            return

    # =================================
    # RELATIONSHIP SYSTEM
    # =================================

    positive_words = [
        "love",
        "miss you",
        "cute",
        "beautiful",
        "pretty",
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

    # =================================
    # NORMAL CHAT
    # =================================

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