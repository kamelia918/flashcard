#This file contains the /start command handler.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import CallbackContext
from data.storage import get_modules
from handlers.utils import get_back_button


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id  # Get the user ID

    modules = get_modules(user_id)
    
    # Create a list of buttons for each module
    keyboard = [
        [InlineKeyboardButton(module, callback_data=f"module_{module}")] for module in modules
    ]
    
    # Add an "Add Module" button
    keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])
    
    # Add a "Back" button
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_modules")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if modules:
        await update.message.reply_text("Your modules:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No modules added yet. Click 'Add Module' to add one.", reply_markup=reply_markup)