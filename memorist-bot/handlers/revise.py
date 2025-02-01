# This file contains the revision-related handlers.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from data.storage import modules

async def list_modules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if modules:
        buttons = [[InlineKeyboardButton(mod, callback_data=f"revise_module_{mod}")] for mod in modules]
        buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.message.reply_text("Please choose a module to revise:", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("No modules available. Please create a module first using /module command.")

revise_handler = CallbackQueryHandler(list_modules, pattern='revise')