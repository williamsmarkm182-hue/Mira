import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv(
    "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"
)

if not GROQ_API_KEY:

    raise ValueError(
        "GROQ_API_KEY is missing"
    )