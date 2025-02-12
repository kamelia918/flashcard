from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
from .module import *
from .cours import handle_list_cours, handle_delete_course, handle_modify_course, handle_add_cours, handle_click_cours
from .revision import *
from .set_revision import *
from .backBTN import *
from .start import start
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review, delete_module, delete_cours, delete_flashcard_by_id
)
from .set_revision_f.start_revision import *
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os

# Import necessary functions from other modules
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
            for f in flashcards:
                if f['front'].startswith('photos/'):
                    # Send the photo
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(f['front'], 'rb'))
                keyboard.append([
                    InlineKeyboardButton(f"Front: {f['front']}", callback_data=f"show_flashcard_{f['id']}"),
                    InlineKeyboardButton("✏️ Modify", callback_data=f"modify_flashcard_{f['id']}"),
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_flashcard_{f['id']}")
                ])
            keyboard.append([InlineKeyboardButton("Back", callback_data=f"modules_{module_name}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Flashcards:", reply_markup=reply_markup)

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    action_type, params = extract_callback_data(query.data)
    if action_type.startswith("add") or action_type.startswith("revise") or action_type.startswith("list") or action_type.startswith("set"):
        context.user_data['initial_action'] = action_type
    clicked_button_data = query.data
    user_id = update.effective_user.id

    if clicked_button_data == "add_module":
        await query.edit_message_text("Type the name of the module you want to add.", reply_markup=back_module_button())
    elif clicked_button_data.startswith("modify_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_modify_module(update, context)
    elif clicked_button_data.startswith("delete_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_delete_module(update, context)
    elif clicked_button_data == "back_to_modules":
        await handle_list_modules(update, context)
    elif clicked_button_data.startswith("module_"):
        await handle_list_cours(update, context)
    elif clicked_button_data.startswith("moduletime_"):
        await handle_list_cours_set_time(update, context)
    elif clicked_button_data.startswith("coursetime_"):
        await handler_list_flashcardupdate_set_time(update, context)
    elif clicked_button_data.startswith("show_flashcard_set_time_"):
        await handler_show_flashcard_set_time(update, context)
    elif clicked_button_data.startswith("course_"):
        await handle_click_cours(update, context)
    elif clicked_button_data.startswith("modify_course_"):
        await handle_modify_course(update, context)
    elif clicked_button_data.startswith("add_course_"):
        await handle_add_cours(update, context)
    elif clicked_button_data.startswith("delete_course_"):
        await handle_delete_course(update, context)
    elif clicked_button_data == "back_to_start":
        await start(update, context)
    elif clicked_button_data.startswith("definir_time_module_"):
        await handle_set_time_module(update, context)
    elif clicked_button_data.startswith("definir_time_cours_"):
        await handle_set_time_course(update, context)
    elif clicked_button_data.startswith("definir_time_flashcard_"):
        await handle_set_time_flashcard(update, context)
    elif clicked_button_data.startswith("select_day_"):
        await select_day(update, context)
    elif clicked_button_data.startswith("selected_date_"):
        await handle_time_input(update, context)
    elif clicked_button_data == "confirm_schedule":
        await confirm_schedule(update, context)
    elif clicked_button_data.startswith("add_hour_"):
        await add_hour(update, context)
    elif clicked_button_data == "palnning":
        await handle_planning_set_time(update, context)
    elif clicked_button_data == "confirm_hour":
        await confirm_hour(update, context)
    elif clicked_button_data.startswith("add_flashcard_"):
        await handle_list_modules(update, context)
    elif clicked_button_data == "list_flashcards_":
        await handle_list_modules(update, context)
    elif clicked_button_data.startswith("revise_"):
        await handle_list_modules(update, context)
    elif clicked_button_data.startswith("set_"):
        await handle_set_Time(update, context)
    elif clicked_button_data == ("listModule_"):
        await handle_list_modules_set_Time(update, context)
    elif clicked_button_data.startswith("show_back_"):
        await handle_show_back(update, context)
    elif clicked_button_data.startswith("next_card_"):
        await handle_next_card(update, context)
    elif clicked_button_data == "restart_revision":
        await handle_restart_revision(update, context)
    elif clicked_button_data.startswith("remembered_") or clicked_button_data.startswith("forgot_"):
        await handle_revision_feedback(update, context)
    elif clicked_button_data.startswith("show_flashcard_"):
        parts = clicked_button_data.split("_")
        if len(parts) == 3:
            _, _, flashcard_id = parts
            module_name = context.user_data.get('module_name')
            course_name = context.user_data.get('course_name')
            if not module_name or not course_name:
                await query.edit_message_text("Erreur : Module ou cours non spécifié.")
                return
            user_id = update.effective_user.id
            all_flashcards = get_flashcards(module_name, course_name, user_id)
            flashcard = next((f for f in all_flashcards if str(f['id']) == flashcard_id), None)
            if flashcard:
                if flashcard['front'].startswith('photos/'):
                    # Send the photo
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(flashcard['front'], 'rb'), caption=f"Back: {flashcard['back']}")
                else:
                    await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}", reply_markup=back_module_button())
            else:
                await query.edit_message_text("Flashcard not found.", reply_markup=back_module_button())
    elif clicked_button_data.startswith("modify_flashcard_"):
        await handle_modify_flashcard(update, context)
    elif clicked_button_data.startswith("delete_flashcard_"):
        await handle_delete_flashcard(update, context)
    elif clicked_button_data.startswith("modify_front"):
        await handle_modify_choice(update, context)
    elif clicked_button_data.startswith("modify_back"):
        await handle_modify_choice(update, context)
    elif clicked_button_data.startswith("modify_both"):
        await handle_modify_choice(update, context)
    elif query.data == "add_text":
        await query.edit_message_text("Veuillez saisir le <b>recto</b> de la carte mémoire.", reply_markup=back_cours_button(), parse_mode="HTML")
    elif query.data == "add_photo":
        await query.edit_message_text("Veuillez envoyer une photo pour le <b>recto</b> de la carte mémoire.", reply_markup=back_cours_button(), parse_mode="HTML")

async def handle_delete_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    if len(parts) == 3:
        flashcard_id = int(parts[2])
        delete_flashcard_by_id(flashcard_id)
        await query.edit_message_text("Flashcard deleted!", reply_markup=back_module_button())

async def handle_modify_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    if len(parts) == 3:
        flashcard_id = int(parts[2])
        context.user_data["modify_flashcard"] = {
            "id": flashcard_id,
            "step": "choose_field"
        }
        keyboard = [
            [InlineKeyboardButton("Front", callback_data="modify_front")],
            [InlineKeyboardButton("Back", callback_data="modify_back")],
            [InlineKeyboardButton("Both", callback_data="modify_both")],
            [InlineKeyboardButton("Back", callback_data=f"back_to_course_{context.user_data.get('current_course')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("What would you like to modify?", reply_markup=reply_markup)

async def handle_modify_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["modify_flashcard"]["choice"] = choice
    if choice == "modify_front":
        await query.edit_message_text("Enter the new FRONT text:")
    elif choice == "modify_back":
        await query.edit_message_text("Enter the new BACK text:")
    elif choice == "modify_both":
        await query.edit_message_text("Enter the new FRONT text first:")
    elif choice == "back_to_course_{context.user_data.get('current_course')}":
        return

def extract_callback_data(callback_data):
    parts = callback_data.split("_")
    action_type = parts[0]
    params = parts[1:]
    return action_type, params

async def error_handler(update: object, context: CallbackContext) -> None:
    print(f"Error: {context.error}")
    if update and update.effective_chat:
        await update.effective_chat.send_message(f"An error occurred: {context.error}")

async def handle_photo(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Create the 'photos' directory if it doesn't exist
    if not os.path.exists('photos'):
        os.makedirs('photos')

    file_path = f"photos/{file.file_id}.jpg"
    await file.download_to_drive(file_path)

    if "flashcard_state" in context.user_data:
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]

        if flashcard_state["step"] == "front":
            context.user_data["flashcard_state"]["front"] = file_path
            context.user_data["flashcard_state"]["step"] = "back"
            await update.message.reply_text("Veuillez maintenant saisir le <b>verso</b> de la carte mémoire. 🔄", reply_markup=back_cours_button(), parse_mode="HTML")
        elif flashcard_state["step"] == "back":
            front = context.user_data["flashcard_state"]["front"]
            back = update.message.text
            result = add_flashcard(module_name, course_name, front, back, user_id)
            if result == "success":
                await update.message.reply_text(f"✅ Flashcard added!\n<b>Front:</b> {front}\n<b>Back:</b> {back}", reply_markup=back_cours_button(), parse_mode="HTML")
            elif result == "duplicate_flashcard":
                await update.message.reply_text(f"Flashcard with front '{front}' already exists in this course.", reply_markup=back_cours_button())
            del context.user_data["flashcard_state"]
