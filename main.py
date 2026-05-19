import os
import random
import time
import telebot

from database import (
    create_user,
    save_chat,
    save_scheduled_message
)

from personality import (
    get_stable_mood,
    update_relationship
)

from memory import (
    process_memory
)

from groq_ai import (
    ask_groq
)

from scheduler import (
    start_scheduler
)

from voice import (
    send_voice_reply
)

from utils import (
    typing_delay,
    human_typo,
    get_toronto_time
)

# =====================================
# BOT TOKEN
# =====================================

BOT_TOKEN = "8782101012:AAGYzaQWr7GYHA9gndaJguVymKuS9KeviUw"

# =====================================
# SETTINGS
# =====================================

ADMIN_ID = 7939923484

REQUIRED_CHANNEL = "starkreport"

# =====================================
# BOT
# =====================================

bot = telebot.TeleBot(
    BOT_TOKEN
)

# =====================================
# START SCHEDULER
# =====================================

start_scheduler(bot)

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
# START COMMAND
# =====================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = str(
        message.from_user.id
    )

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

    welcome_messages = [

        "hey 😭",
        "finally u replied",
        "bro where have u been",
        "hellooo",
        "u seem interesting already 😭"
    ]

    bot.reply_to(
        message,
        random.choice(
            welcome_messages
        )
    )

# =====================================
# MAIN CHAT
# =====================================

@bot.message_handler(func=lambda m: True)
def chat(message):

    user_id = str(
        message.from_user.id
    )

    chat_id = str(
        message.chat.id
    )

    create_user(user_id)

    # =================================
    # FORCE JOIN
    # =================================

    if not joined_required_channel(user_id):

        bot.reply_to(
            message,
            f"""
⚠️ Join @{REQUIRED_CHANNEL} first.

https://t.me/{REQUIRED_CHANNEL}
"""
        )

        return

    # =================================
    # USER TEXT
    # =================================

    text = ""

    if message.text:

        text = message.text.lower()

    # =================================
    # PHOTO REPLIES
    # =================================

    if message.photo:

        photo_replies = [

            "wait this actually looks good 😭",
            "okay this goes hard",
            "bro what is this image 😭",
            "lowkey like this",
            "nah this kinda fire"
        ]

        bot.reply_to(
            message,
            random.choice(
                photo_replies
            )
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
    # MEMORY SYSTEM
    # =================================

    process_memory(
        user_id,
        text
    )

    # =================================
    # RELATIONSHIP SYSTEM
    # =================================

    relationship_level = update_relationship(
        user_id,
        text
    )

    # =================================
    # TIME QUESTIONS
    # =================================

    time_questions = [

        "what time is it",
        "what's the time",
        "whats the time",
        "toronto time",
        "are you awake",
        "you awake"
    ]

    if any(
        q in text
        for q in time_questions
    ):

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

        extra = random.choice([

            "i should probably sleep 😭",
            "still awake somehow",
            "toronto vibes rn",
            "i'm lowkey tired"
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
                text.replace(
                    "text me in",
                    ""
                )
                .replace(
                    "minutes",
                    ""
                )
                .replace(
                    "minute",
                    ""
                )
                .replace(
                    "mins",
                    ""
                )
                .replace(
                    "min",
                    ""
                )
                .strip()
            )

            mins = int(
                mins_text
            )

            future_message = random.choice([

                "heyy 😭",
                "still alive?",
                "u disappeared again",
                "soo what are u doing now",
                "you awake?",
                "bro answer me 😭"
            ])

            send_time = int(
                time.time()
            ) + (
                mins * 60
            )

            save_scheduled_message(

                user_id,
                chat_id,
                future_message,
                send_time
            )

            bot.reply_to(
                message,
                f"okay i'll text u in {mins} minute(s) 😭"
            )

            return

        except Exception as e:

            print(e)

            bot.reply_to(
                message,
                "say it like: text me in 5 minutes"
            )

            return

    # =================================
    # GET MOOD
    # =================================

    mood = get_stable_mood(
        user_id
    )

    # =================================
    # TYPING ACTION
    # =================================

    bot.send_chat_action(
        chat_id,
        "typing"
    )

    typing_delay(text)

    # =================================
    # AI REPLY
    # =================================

    try:

        reply = ask_groq(

            user_id,
            text,
            mood,
            relationship_level
        )

        reply = human_typo(
            reply
        )

        # =============================
        # RANDOM VOICE NOTE
        # =============================

        if random.randint(1, 100) <= 10:

            send_voice_reply(

                bot,
                chat_id,
                reply
            )

        else:

            bot.reply_to(
                message,
                reply
            )

        # =============================
        # SAVE BOT CHAT
        # =============================

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
# BOT ONLINE
# =====================================

print(
    "Mira is online..."
)

# =====================================
# RUN BOT
# =====================================

bot.infinity_polling()