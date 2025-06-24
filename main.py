import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import speech_recognition as sr
from pydub import AudioSegment

# הגדר לוגים
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Send me a voice message in English and I will correct your mistakes.")

def handle_voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    wav_path = "voice.wav"
    file.download(file_path)

    # המרה ל־WAV
    sound = AudioSegment.from_file(file_path)
    sound.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            update.message.reply_text(f"You said: {text}")
            # כאן אפשר להוסיף בדיקת שגיאות ודקדוק
        except sr.UnknownValueError:
            update.message.reply_text("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            update.message.reply_text(f"Speech recognition error: {e}")

def main():
    updater = Up
