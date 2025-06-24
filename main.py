
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
import tempfile
from gtts import gTTS

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please send me a voice message in English.")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.voice.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tf:
        await file.download_to_drive(tf.name)
        recognizer = sr.Recognizer()
        with sr.AudioFile(tf.name) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                await update.message.reply_text(f"You said: {text}")
                tts = gTTS(text="Well said!", lang='en')
                tts_fp = tf.name.replace(".oga", ".mp3")
                tts.save(tts_fp)
                with open(tts_fp, 'rb') as voice_file:
                    await update.message.reply_voice(voice_file)
            except sr.UnknownValueError:
                await update.message.reply_text("Sorry, I couldn't understand.")
            except Exception as e:
                await update.message.reply_text(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

app.run_polling()
