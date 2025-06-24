import logging
import os
import tempfile
import speech_recognition as sr
from gtts import gTTS

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please send me a voice message in English.")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # הורדת ההודעה הקולית מהשרת של טלגרם
        file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tf:
            await file.download_to_drive(tf.name)

        # המרה לקול קריא
        recognizer = sr.Recognizer()
        with sr.AudioFile(tf.name) as source:
            audio = recognizer.record(source)

        try:
            # זיהוי טקסט מהקלט
            text = recognizer.recognize_google(audio)
            await update.message.reply_text(f"You said: {text}")

            # יצירת תגובה קולית
            tts = gTTS(text="Well said!", lang='en')
            mp3_path = tf.name.replace(".oga", ".mp3")
            tts.save(mp3_path)

            # שליחת תגובה קולית
            with open(mp3_path, 'rb') as voice_file:
                await update.message.reply_voice(voice_file)

        except sr.UnknownValueError:
            await update.message.reply_text("Sorry, I couldn't understand.")
        except Exception as e:
            await update.message.reply_text(f"Recognition error: {e}")

    except Exception as e:
        await update.message.reply_text(f"Download error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.run_polling()
