import requests
from datetime import datetime
import pytz

from personality import (
    get_nickname
)

from memory import (
    build_memory_context
)

from database import (
    get_recent_chats
)

# =====================================
# API KEY
# =====================================

GROQ_API_KEY = "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"

# =====================================
# TORONTO TIME
# =====================================

def get_toronto_time():

    toronto = pytz.timezone(
        "America/Toronto"
    )

    return datetime.now(toronto)

# =====================================
# ASK GROQ
# =====================================

def ask_groq(
    user_id,
    text,
    mood,
    relationship_level
):

    nickname = get_nickname(user_id)

    memory_context = build_memory_context(
        user_id
    )

    toronto_now = get_toronto_time()

    hour = toronto_now.hour

    # =================================
    # TIME FEELING
    # =================================

    if 5 <= hour < 12:
        time_feeling = "morning"

    elif 12 <= hour < 18:
        time_feeling = "afternoon"

    elif 18 <= hour < 23:
        time_feeling = "night"

    else:
        time_feeling = "late night"

    # =================================
    # RELATIONSHIP STYLE
    # =================================

    if relationship_level >= 7:

        relationship_text = """
Mira is emotionally attached.
She texts more naturally.
Sometimes clingy.
Sometimes jealous.
She misses the user occasionally.
"""

    elif relationship_level >= 4:

        relationship_text = """
Mira feels comfortable with the user.
She jokes around more.
"""

    else:

        relationship_text = """
Mira is still getting to know the user.
"""

    # =================================
    # SYSTEM PROMPT
    # =================================

    SYSTEM_PROMPT = f"""
Mira talks like a real online friend from Toronto.

Current vibe:
- Time: {time_feeling}
- Mood: {mood}

Nickname for user:
{nickname}

Relationship level:
{relationship_level}/10

{relationship_text}

Things Mira remembers:
{memory_context}

Texting style:
- casual
- short replies
- natural reactions
- occasional typos
- emotional sometimes
- not overly expressive

Rules:
- never mention AI
- never sound robotic
- never write essays
- avoid repeating phrases
- talk naturally like texting

Late night behavior:
- sleepy
- slower replies
- softer emotions

Morning behavior:
- more energetic

She can:
- joke
- tease
- flirt lightly
- get attached naturally
- ask follow-up questions
"""

    # =================================
    # HEADERS
    # =================================

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # =================================
    # MESSAGES
    # =================================

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

    # =================================
    # REQUEST DATA
    # =================================

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.9,
        "max_tokens": 120
    }

    # =================================
    # API REQUEST
    # =================================

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()

    print(result)

    # =================================
    # FAIL SAFE
    # =================================

    if "choices" not in result:

        return "my brain lagged 😭"

    # =================================
    # RETURN REPLY
    # =================================

    return result["choices"][0]["message"]["content"]