import os
import logging
import random
import tempfile
import speech_recognition as sr
from gtts import gTTS

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# רשימת משפטים לתרגול
PRACTICE_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How are you doing today?",
    "English is fun to learn.",
    "Can you repeat after me?"
]

# פונקציית התחלה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence = random.choice(PRACTICE_SENTENCES)
    context.user_data["current_sentence"] = sentence

    # שליחת המשפט בטקסט
    await update.message.reply_text(f"Repeat this sentence:\n\n{sentence}")

    # הפקת קול מהמשפט
    tts = gTTS(text=sentence, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        with open(f.name, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file)

    await update.message.reply_text("Now send me your voice saying the same sentence!")

# קליטת הודעת קול והשוואת ההגייה
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # הורדת ההודעה הקולית
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tf:
            await file.download_to_drive(tf.name)

            # זיהוי דיבור
            recognizer = sr.Recognizer()
            with sr.AudioFile(tf.name) as source:
                audio = recognizer.record(source)
                try:
                    user_text = recognizer.recognize_google(audio)
                    original = context.user_data.get("current_sentence", "").lower()
                    spoken = user_text.lower()

                    # חישוב אחוז התאמה פשוט (על סמך התאמת מילים)
                    original_words = set(original.split())
                    spoken_words = set(spoken.split())
                    match = len(original_words & spoken_words)
                    total = len(original_words)
                    score = int((match / total) * 100) if total > 0 else 0

                    await update.message.reply_text(
                        f"You said: {user_text}\nAccuracy: {score}%"
                    )
                except sr.UnknownValueError:
                    await update.message.reply_text("Sorry, I couldn't understand what you said.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# בניית האפליקציה והפעלתה
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

app.run_polling()
