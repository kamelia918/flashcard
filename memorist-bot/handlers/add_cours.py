# This file contains the /cours command handler.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from data.storage import modules

async def add_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if modules:
        buttons = [[InlineKeyboardButton(mod, callback_data=f"add_cours_module_{mod}")] for mod in modules]
        buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Please choose the module to add the cours:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No modules available. Please create a module first using /module command.")

add_cours_handler = CommandHandler("cours", add_cours)