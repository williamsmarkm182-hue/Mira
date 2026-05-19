from database import (
    save_memory,
    get_memories
)

# =====================================
# DETECT IMPORTANT MEMORIES
# =====================================

def process_memory(user_id, text):

    text = text.lower()

    memory_triggers = [

        ("i like", "Likes"),
        ("my favorite", "Favorite"),
        ("i love", "Loves"),
        ("i hate", "Hates"),
        ("my birthday", "Birthday"),
        ("i'm from", "From"),
        ("i am from", "From"),
        ("i play", "Plays"),
        ("i work", "Works"),
        ("i study", "Studies"),
        ("my exam", "Has exam"),
        ("i have exam", "Has exam"),
        ("my girlfriend", "Has girlfriend"),
        ("my boyfriend", "Has boyfriend"),
        ("i miss", "Misses"),
        ("i feel", "Feels")
    ]

    for trigger, label in memory_triggers:

        if trigger in text:

            memory = f"{label}: {text}"

            existing_memories = get_memories(user_id)

            if memory not in existing_memories:

                save_memory(
                    user_id,
                    memory
                )

            return

# =====================================
# FORMAT MEMORIES
# =====================================

def build_memory_context(user_id):

    memories = get_memories(user_id)

    if not memories:
        return "No important memories yet."

    return "\n".join(memories)