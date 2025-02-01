#This file contains the /module command handler.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

async def add_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_step'] = 'add_module'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Please enter the name of the new module.", reply_markup=reply_markup)

add_module_handler = CommandHandler("module", add_module)