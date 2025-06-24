import os
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import speech_recognition as sr
import tempfile
import requests
import difflib

# הגדרת משפטים לתרגול
PRACTICE_SENTENCES = [
    "She sells seashells by the seashore.",
    "The quick brown fox jumps over the lazy dog.",
    "I think I can, I think I can, I think I can.",
    "Peter Piper picked a peck of pickled peppers.",
]

# זיהוי קולי
recognizer = sr.Recognizer()

# התחלה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentence = PRACTICE_SENTENCES[0]
    context.user_data["sentence_index"] = 0
    await update.message.reply_text(f"Repeat this sentence:\n\n{sentence}")
    await update.message.reply_text("Now send me your voice saying the same sentence!")

# קליטת הודעה קולית
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "sentence_index" not in context.user_data:
        await update.message.reply_text("Please start with /start")
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
