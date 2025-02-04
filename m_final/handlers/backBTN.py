from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def get_back_button():
    # Helper function to create a "Back" button
    keyboard = [[InlineKeyboardButton("Back", callback_data="back_to_modules")]]
    return InlineKeyboardMarkup(keyboard)
