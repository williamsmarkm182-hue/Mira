import os
import random
from gtts import gTTS

# =====================================
# VOICE REPLIES
# =====================================

def generate_voice(text):

    # RANDOM HUMAN STYLE

    starters = [
        "",
        "brooo ",
        "okay so ",
        "wait 😭 ",
        "nah because "
    ]

    text = random.choice(starters) + text

    # CREATE TTS

    tts = gTTS(
        text=text,
        lang="en",
        slow=False
    )

    # RANDOM FILE NAME

    filename = f"voice_{random.randint(1000,9999)}.mp3"

    # SAVE AUDIO

    tts.save(filename)

    return filename

# =====================================
# SEND VOICE
# =====================================

def send_voice_reply(bot, chat_id, text):

    try:

        filename = generate_voice(text)

        with open(filename, "rb") as audio:

            bot.send_voice(
                chat_id,
                audio
            )

        # DELETE FILE AFTER SEND

        os.remove(filename)

    except Exception as e:

        print(e)