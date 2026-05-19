import random
import time
from datetime import datetime
import pytz

# =====================================
# TORONTO TIME
# =====================================

def get_toronto_time():

    toronto = pytz.timezone(
        "America/Toronto"
    )

    return datetime.now(toronto)

# =====================================
# HUMAN TYPING DELAY
# =====================================

def typing_delay(text):

    # BASED ON MESSAGE LENGTH

    delay = len(text) / 12

    # LIMITS

    if delay < 1.5:
        delay = 1.5

    if delay > 8:
        delay = 8

    # RANDOMNESS

    delay += random.uniform(
        0.2,
        1.5
    )

    time.sleep(delay)

# =====================================
# HUMAN TYPOS
# =====================================

def human_typo(text):

    if random.randint(1, 100) > 25:
        return text

    replacements = {

        "you": "u",
        "really": "rlly",
        "please": "pls",
        "okay": "okayy",
        "bro": "brooo",
        "what": "wat",
        "love": "luv",
        "going to": "gonna",
        "i am": "i'm"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text

# =====================================
# RANDOM HUMAN REACTIONS
# =====================================

def random_reaction():

    reactions = [

        "😭",
        "😂",
        "brooo",
        "nah",
        "lowkey",
        "LMFAOO",
        "wait",
        "HELP 😭"
    ]

    return random.choice(reactions)

# =====================================
# TIME FEELING
# =====================================

def get_time_feeling():

    now = get_toronto_time()

    hour = now.hour

    if 5 <= hour < 12:
        return "morning"

    elif 12 <= hour < 18:
        return "afternoon"

    elif 18 <= hour < 23:
        return "night"

    else:
        return "late night"

# =====================================
# RANDOM STATUS
# =====================================

def fake_human_status():

    statuses = [

        "eating rn",
        "trying not to sleep 😭",
        "watching tiktok",
        "half asleep",
        "charging my phone",
        "listening to music",
        "doing nothing honestly",
        "bored asf"
    ]

    return random.choice(statuses)