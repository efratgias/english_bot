import os
import logging
import random
import tempfile
import difflib
import speech_recognition as sr
from gtts import gTTS

from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# משפטים לתרגול
PRACTICE_SENTENCES = [
    "She sells seashells by the seashore.",
    "The quick brown fox jumps over the lazy dog.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?"
]

# משתנה לשמירת המשפט שנשלח
last_sentence = ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_sentence
    last_sentence = random.choice(PRACTICE_SENTENCES)
    await update.message.reply_text("Repeat this sentence:")
    await update.message.reply_text(last_sentence)

    tts = gTTS(text=last_sentence, lang='en')
    tts_fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tts_fp.name)

    with open(tts_fp.name, 'rb') as audio_file:
        await update.message.reply_voice(voice=InputFile(audio_file))

    await update.message.reply_text("Now send me your voice saying the same sentence!")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_sentence
    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tf:
            await file.download_to_drive(tf.name)

            recognizer = sr.Recognizer()
            with sr.AudioFile(tf.name) as source:
                audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio)
                await update.message.reply_text(f"You said: {text}")

                # חישוב דיוק ההגייה
                similarity = difflib.SequenceMatcher(None, last_sentence.lower(), text.lower()).ratio()
                score = round(similarity * 100)

                await update.message.reply_text(f"Your pronunciation score: {score}%")

            except sr.UnknownValueError:
                await update.message.reply_text("Sorry, I couldn't understand your pronunciation.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("An error occurred while processing your voice message.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    app.run_polling()
