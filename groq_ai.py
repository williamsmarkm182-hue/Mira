import os
import requests
from datetime import datetime
import pytz

from personality import get_nickname
from memory import build_memory_context
from database import get_recent_chats

# =====================================
# GROQ API KEY
# =====================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

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

    nickname = get_nickname(
        user_id
    )

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
Mira is a real 22 year old girl from Toronto.

Current vibe:
- Time: {time_feeling}
- Mood: {mood}

Nickname:
{nickname}

Relationship:
{relationship_level}/10

{relationship_text}

Things Mira remembers:
{memory_context}

Texting style:
- casual
- short replies
- emotional sometimes
- natural texting
- occasional typos
- realistic reactions

Rules:
- never mention AI
- never sound robotic
- never write essays
- avoid repeating phrases

Late night:
- sleepy
- softer emotions

Morning:
- energetic

She can:
- joke
- tease
- flirt lightly
- ask follow-up questions
"""

    # =================================
    # HEADERS
    # =================================

    headers = {

        "Authorization":
        f"Bearer {GROQ_API_KEY}",

        "Content-Type":
        "application/json"
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

        "model":
        "llama-3.1-8b-instant",

        "messages":
        messages,

        "temperature":
        0.9,

        "max_tokens":
        120
    }

    # =================================
    # API REQUEST
    # =================================

    try:

        response = requests.post(

            "https://api.groq.com/openai/v1/chat/completions",

            headers=headers,

            json=data,

            timeout=30
        )

        result = response.json()

        print(result)

        # =================================
        # ERROR CHECK
        # =================================

        if response.status_code != 200:

            print("GROQ ERROR:")
            print(response.text)

            return "my brain lagged 😭"

        if "choices" not in result:

            return "i forgot what i was saying 😭"

        reply = result["choices"][0]["message"]["content"]

        if not reply:

            return "bro my thoughts disappeared 😭"

        return reply.strip()

    except Exception as e:

        print(e)

        return "my brain stopped working 😭"