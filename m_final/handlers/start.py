#This file contains the /start command handler.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import CallbackContext
from data.storage import get_modules
from handlers.utils import get_back_button
from .utils import extract_callback_data

async def start(update: Update, context: CallbackContext) -> None:
    keyboard=[]
    # Create a list of buttons for each module
    keyboard.append([InlineKeyboardButton("➕ Ajouter une carte", callback_data="add_flashcard_")])
    keyboard.append([InlineKeyboardButton("📖 Réviser", callback_data="revise_")])
    keyboard.append([InlineKeyboardButton("🗂️ Liste des cartes", callback_data="list_flashcards_")])
    keyboard.append([InlineKeyboardButton("⏰ Définir l'heure de révision", callback_data="set_revise_hour")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message=""" Bienvenue sur <b>Memorist</b>, un bot Telegram spécialement conçu pour vous aider à mémoriser et à retenir des informations sur le long terme grâce à la méthode du rappel actif.  

Pour optimiser votre apprentissage, nous vous recommandons d’utiliser la technique de la répétition espacée, qui améliore considérablement la rétention des connaissances.  
- ajouter instructions 
🎥 <b>Vidéo explicative</b> : [Ajoutez votre lien ici]  

N’hésitez pas à nous faire part de vos retours ! Bonne révision et visez l’excellence 😃✨"""
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")

