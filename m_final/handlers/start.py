#This file contains the /start command handler.
from telegram import Bot, BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import CallbackContext


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
    # await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
    if update.message:  # Called via /start command
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")
        #  No initial_action set here.  It's set on the *button click*.
    elif update.callback_query:  # Called by clicking the "Back" button
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
        # Again, no initial_action set here
    #else:  # Should not happen, but good to have a default case
        #await update.message.reply_text("Unexpected update type.")


async def set_commands(bot: Bot):
    """Sets the bot's commands, which appear in the menu."""
    commands = [
        BotCommand(command="start", description="Start the bot"),
            ]
    await bot.set_my_commands(commands)
