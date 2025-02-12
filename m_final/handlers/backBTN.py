from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def back_module_button():
    # Helper function to create a "Back" button
    keyboard = [[InlineKeyboardButton("Back", callback_data="back_to_modules")]]
    return InlineKeyboardMarkup(keyboard)

def back_cours_button():
    # Helper function to create a "Back" button
    keyboard = [[InlineKeyboardButton("Back", callback_data="modules_")]]
    return InlineKeyboardMarkup(keyboard)



# BACK TO MODULE ADD 
# BACK TO MODULES SET TIME 