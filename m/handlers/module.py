from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.storage import add_module, get_modules

async def handle_add_module(update: Update, context: CallbackContext) -> None:
    module_name = update.message.text
    add_module(module_name)  # Add the module to storage
    
    modules = get_modules()
    
    # Create a list of buttons for each module
    keyboard = [
        [InlineKeyboardButton(module, callback_data=f"module_{module}")] for module in modules
    ]
    
    # Add an "Add Module" button
    keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"Module '{module_name}' added!", reply_markup=reply_markup)