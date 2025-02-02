#This file contains the /start command handler.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import CallbackContext
from data.storage import get_modules
from handlers.utils import get_back_button


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    modules = get_modules(user_id)

    if not modules:
        await update.message.reply_text("No modules found. Click 'Add Module' to add one.", reply_markup=get_back_button())
        return

    # Create a list of buttons for each module
    keyboard = []
    for module in modules:
        keyboard.append([
            InlineKeyboardButton(module, callback_data=f"module_{module}"),
            InlineKeyboardButton("✏️ Modify", callback_data=f"modify_module_{module}"),
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_module_{module}")
        ])

    # Add an "Add Module" button
    keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Your modules:", reply_markup=reply_markup)
