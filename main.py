import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import whisper
from gtts import gTTS
import os
from pydub import AudioSegment
import difflib
import configparser

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

API_TOKEN = config["telegram"]["bot_token"]
ORIGINAL_SENTENCE = "The quick brown fox jumps over the lazy dog"

# Load Whisper model
model = whisper.load_model("base")

# Logger
logging.basicConfig(level=logging.INFO)

# Save TTS
def save_tts(sentence, path):
    tts = gTTS(text=sentence, lang="en")
    tts.save(path)

# Pronunciation score
def get_score(original: str, spoken: str) -> int:
    matcher = difflib.SequenceMatcher(None, original.lower(), spoken.lower())
    return int(matcher.ratio() * 100)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Repeat this sentence:\n\n{ORIGINAL_SENTENCE}")
    save_tts(ORIGINAL_SENTENCE, "reference.mp3")
    await update.message.reply_voice(voice=InputFile("reference.mp3"))

# Handle voice message
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = "user.ogg"
    await file.download_to_drive(file_path)

    # Convert to wav
    audio = AudioSegment.from_file(file_path)
    audio.export("user.wav", format="wav")

    # Transcribe
    result = model.transcribe("user.wav", language="en")
    user_text = result["text"]

    # Score
    score = get_score(ORIGINAL_SENTENCE, user_text)

    await update.message.reply_text(f"You said: {user_text}\nPronunciation score: {score}%")

# Main app
def main():
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
