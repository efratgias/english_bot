import os
from pyrogram import Client, filters
import speech_recognition as sr
from pydub import AudioSegment

api_id = int(os.environ['api_id'])
api_hash = os.environ['api_hash']
bot_token = os.environ['BOT_TOKEN']

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def recognize_speech(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_ogg(file_path)
    wav_path = file_path.replace(".ogg", ".wav")
    audio.export(wav_path, format="wav")

    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "I couldn't understand what you said."
        except sr.RequestError:
            return "Sorry, there's a problem with the recognition service."

@app.on_message(filters.voice)
def voice_handler(client, message):
    file = app.download_media(message.voice.file_id)
    text = recognize_speech(file)
    message.reply_text(f"You said: {text}")

app.run()
