import os
import tempfile
import random
import logging
import speech_recognition as sr
from gtts import gTTS

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

sentences = [
    "She sells seashells by the seashore.",
    "I thought I saw a pussycat.",
    "How much wood would a woodchuck chuck?",
    "The quick brown fox jumps over the lazy dog.",
    "Peter Piper picked a peck of pickled peppers."
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence = random.choice(sentences)
    context.user_data["current_sentence"] = sentence

    # שליחת הטקסט
    await update.message.reply_text(f"Repeat this sentence:\n\n{sentence}")

    # יצירת קול
    tts = gTTS(sentence)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        with open(f.name, "rb") as audio_file:
            await update.message.reply_voice(voice=InputFile(audio_file))

    # בקשה מהמשתמש להקליט
    await update.message.reply_text("Now send me your voice saying the same sentence!")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tf:
            await file.download_to_drive(tf.name)

            recognizer = sr.Recognizer()
            with sr.AudioFile(tf.name) as source:
                audio = recognizer.record(source)

            user_text = recognizer.recognize_google(audio)
            await update.message.reply_text(f"You said: {user_text}")

            expected = context.user_data.get("current_sentence", "")
            expected_words = expected.lower().split()
            user_words = user_text.lower().split()
            matches = sum(1 for w1, w2 in zip(expected_words, user_words) if w1 == w2)
            accuracy = round((matches / len(expected_words)) * 100) if expected_words else 0

            await update.message.reply_text(f"Pronunciation Accuracy: {accuracy}%")
            await update.message.reply_text("Want to try again? Type /start")

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Sorry, I couldn't understand. Please try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.run_polling()
