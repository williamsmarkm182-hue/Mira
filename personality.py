import random

from database import (
    get_user,
    cursor,
    conn
)

# =====================================
# GET NICKNAME
# =====================================

def get_nickname(user_id):

    user = get_user(user_id)

    nickname = user[3]

    if nickname and nickname != "":
        return nickname

    names = [
        "bro",
        "sleepyhead",
        "dummy",
        "angel",
        "gremlin",
        "clingy human",
        "menace 😭"
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
# STABLE MOOD SYSTEM
# =====================================

def get_stable_mood(user_id):

    moods = [
        "friendly",
        "playful",
        "sleepy",
        "clingy",
        "calm",
        "curious",
        "jealous"
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

    # FIRST TIME

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

    # SMALL CHANCE TO CHANGE

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
# UPDATE RELATIONSHIP
# =====================================

def update_relationship(user_id, text):

    positive_words = [
        "love",
        "miss you",
        "cute",
        "beautiful",
        "pretty",
        "goodnight",
        "good morning",
        "i need you",
        "mwah",
        "kiss"
    ]

    negative_words = [
        "leave me alone",
        "annoying",
        "hate you",
        "shut up",
        "go away"
    ]

    user = get_user(user_id)

    relationship_level = user[2]

    text = text.lower()

    # POSITIVE

    if any(word in text for word in positive_words):

        relationship_level += 1

    # NEGATIVE

    if any(word in text for word in negative_words):

        relationship_level -= 1

    # LIMITS

    if relationship_level < 0:
        relationship_level = 0

    if relationship_level > 10:
        relationship_level = 10

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

    return relationship_level

# =====================================
# HUMAN TYPOS
# =====================================

def humanize_text(text):

    if random.randint(1, 100) > 25:
        return text

    replacements = {
        "you": "u",
        "really": "rlly",
        "please": "pls",
        "okay": "okayy",
        "laughing": "dying 😭",
        "bro": "brooo"
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text