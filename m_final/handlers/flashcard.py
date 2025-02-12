from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .backBTN import back_cours_button
from .revision import show_next_flashcard
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review, delete_module, delete_cours, delete_flashcard_by_id
)

async def handler_add_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 3:
        _, module_name, course_name = parts
        context.user_data["flashcard_state"] = {
            "module": module_name,
            "course": course_name,
            "step": "front"
        }
        keyboard = [
            [InlineKeyboardButton("📝 Texte", callback_data="add_text")],
            [InlineKeyboardButton("📸 Photo", callback_data="add_photo")],
            [InlineKeyboardButton("🔙 Retour", callback_data=f"course_{module_name}_{course_name}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choisissez le type de contenu pour le recto de la carte mémoire.", reply_markup=reply_markup, parse_mode="HTML")

async def handler_list_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 3:
        _, module_name, course_name = parts
        flashcards = get_flashcards(module_name, course_name, user_id)
        keyboard = []
        keyboard.append([InlineKeyboardButton("Back", callback_data=f"course_{module_name}_{course_name}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        if not flashcards:
            await query.edit_message_text("No flashcards found.", reply_markup=reply_markup)
        else:
            keyboard = [
                [
                    InlineKeyboardButton(f"Front: {f['front']}", callback_data=f"show_flashcard_{f['id']}"),
                    InlineKeyboardButton("✏️ Modify", callback_data=f"modify_flashcard_{f['id']}"),
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_flashcard_{f['id']}")
                ]
                for f in flashcards
            ]
            keyboard.append([InlineKeyboardButton("Back", callback_data=f"modules_{module_name}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Flashcards:", reply_markup=reply_markup)
