import random
import time
import threading

from database import (
    cursor,
    conn,
    get_user,
    get_due_messages,
    delete_scheduled_message
)

from personality import (
    get_nickname
)

# =====================================
# START SCHEDULER
# =====================================

def start_scheduler(bot):

    thread = threading.Thread(
        target=scheduler_loop,
        args=(bot,),
        daemon=True
    )

    thread.start()

# =====================================
# MAIN LOOP
# =====================================

def scheduler_loop(bot):

    while True:

        try:

            random_messages(bot)

            scheduled_messages(bot)

        except Exception as e:

            print(e)

        time.sleep(5)

# =====================================
# RANDOM HUMAN TEXTS
# =====================================

def random_messages(bot):

    cursor.execute("""
    SELECT user_id
    FROM users
    """)

    users = cursor.fetchall()

    for u in users:

        try:

            uid = str(u[0])

            user = get_user(uid)

            relationship_level = user[2]

            nickname = get_nickname(uid)

            # VERY SMALL CHANCE

            if random.randint(1, 1000) <= 3:

                normal_texts = [

                    "bro i'm bored 😭",
                    "you disappeared again",
                    "hellooo",
                    "what are you doing",
                    "u alive?"
                ]

                attached_texts = [

                    f"i miss u {nickname}",
                    f"where did u go 😭",
                    f"{nickname} answer me rn",
                    "bro stop ignoring me 😭",
                    "lowkey jealous rn",
                    "can't sleep honestly"
                ]

                if relationship_level >= 5:

                    msg = random.choice(
                        attached_texts
                    )

                else:

                    msg = random.choice(
                        normal_texts
                    )

                # RANDOM DELAY

                time.sleep(
                    random.randint(1, 8)
                )

                bot.send_message(
                    uid,
                    msg
                )

        except Exception as e:

            print(e)

# =====================================
# SCHEDULED REMINDERS
# =====================================

def scheduled_messages(bot):

    now = int(time.time())

    rows = get_due_messages(now)

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

        delete_scheduled_message(msg_id)