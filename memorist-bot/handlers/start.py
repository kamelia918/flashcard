#This file contains the /start command handler.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [InlineKeyboardButton("Add a card", callback_data='add_card')],
        [InlineKeyboardButton("Revise", callback_data='revise')],
        [InlineKeyboardButton("Set timer for revision", callback_data='set_timer')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Welcome to Memorist, a telegram bot specially developed to help you with recalling information...",
        reply_markup=reply_markup
    )

start_handler = CommandHandler("start", start)