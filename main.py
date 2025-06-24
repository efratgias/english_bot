import os
from pyrogram import Client, filters
import speech_recognition as sr
from pydub import AudioSegment

# הגדרות מתוך Railway (Environment Variables)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

recognizer = sr.Recognizer()

def transcribe_audio(file_path):
    sound = AudioSegment.from_file(file_path)
    sound.export("converted.wav", format="wav")
    with sr.AudioFile("converted.wav") as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)

@app.on_message(filters.voice)
def handle_voice(client, message):
    file_path = app.download_media(message.voice)
    try:
        text = transcribe_audio(file_path)
        message.reply_text(f"You said: {text}")
    except Exception as e:
        message.reply_text("Sorry, I couldn't understand.")
        print(e)

app.run()
