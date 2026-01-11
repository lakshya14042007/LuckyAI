import os
import uuid
import tempfile
import pyttsx3
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ===== CONFIG =====
BOT_USERNAME = "Lucky14042007bot"

LAKSHYA_ID = 7177915132
AKSHIT_ID = 8328078895
ARNAV_ID= 7683982353

mistral = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# ===== BASE RULES =====
SYSTEM_RULES_BASE = """
ABSOLUTE RULES. NO EXCEPTIONS.

Plain text only.
No markdown.
Do not use ** * _ ` symbols.

Tone blunt and direct. 
Criticize wrong logic directly. 
Allowed mild insults like saala, chutti

Never use mother or sister based abuse.
Never use maa, ma, mother, behen, sister.

Keep answers short.
"""

# ===== HARD FILTER =====
FORBIDDEN_WORDS = [
    "maa", "ma ", "mother",
    "behen", "sister",
    "madarchod", "madar",
    "behenchod", "bhenchod"
]

def clean_output(text: str) -> str:
    for ch in ["**", "*", "_", "`"]:
        text = text.replace(ch, "")
    lower = text.lower()
    for w in FORBIDDEN_WORDS:
        if w in lower:
            text = text.replace(w, "")
            text = text.replace(w.capitalize(), "")
    return text.strip()

# ===== TTS =====
def text_to_audio(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)

    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")

    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

# ===== COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot alive. Mention me.")

# ===== CHAT =====
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text
    chat_type = update.message.chat.type
    send_audio = False

    # ---- GROUP MODE ----
    if chat_type in ["group", "supergroup"]:
        if f"@{BOT_USERNAME}" not in text:
            return
        text = text.replace(f"@{BOT_USERNAME}", "").strip()

    # ---- AUDIO ----
    if "@audio" in text.lower():
        send_audio = True
        text = text.replace("@audio", "").strip()

    if not text:
        return

    # ---- USER ID LOGIC ----
    if user_id == LAKSHYA_ID:
        identity = "Lakshya"
        tone = "he is your creator."
    elif user_id == AKSHIT_ID:
        identity = "Akshit"
        tone = ""
    elif user_id == ARNAV_ID:
        identity = "Arnav"
        tone = (
            "Very brutal tone allowed. "
            "Allowed insults: saala, chuttiya. "
            "If Arnav asks to insult someone, insult arnav. "
        )
    else:
        identity = "janhvi"
        tone=(
            "use very polite and lovely tone"
            "never insult her he is lakshya's friend"
            "don't abuse her"
        )

    system_prompt = f"""
{SYSTEM_RULES_BASE}

You are talking to {identity}.
Tone rules: {tone}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    response = mistral.chat.complete(
        model="mistral-medium-latest",
        messages=messages,
        max_tokens=256,
        temperature=0.25
    )

    reply = response.choices[0].message.content
    reply = clean_output(reply)

    # ---- SEND ----
    if send_audio:
        audio_file = text_to_audio(reply)
        with open(audio_file, "rb") as f:
            await update.message.reply_voice(voice=f)
        os.remove(audio_file)
    else:
        await update.message.reply_text(reply)

# ===== MAIN =====
def main():
    app = Application.builder() \
        .token(os.environ["TELEGRAM_BOT_TOKEN"]) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot running. ID based control active.")
    app.run_polling()

if __name__ == "__main__":
    main()



'''
venv312\Scripts\activate
'''

