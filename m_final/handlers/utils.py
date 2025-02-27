from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
import random
import os
import re  # 📌 Importer re pour extraire le chemin de l'image
import calendar
from .module import *
from .cours import handle_list_cours, handle_delete_course, handle_modify_course, handle_add_cours, handle_click_cours
from .revision import *
from .set_revision import *
from .backBTN import *
from .start import start
from .flashcard import handle_delete_flashcard, handle_modify_choice,  handler_list_flashcardupdate
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review, delete_module, delete_cours, delete_flashcard_by_id
)
from .flashcard import handle_delete_flashcard, handle_modify_choice, handle_modify_flashcard,handle_show_flashcard, handler_list_flashcardupdate
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review,delete_module , delete_cours,delete_flashcard_by_id
)
from .set_revision_f.start_revision import *

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    action_type, params = extract_callback_data(query.data)

    if action_type.startswith("add") or action_type.startswith("revise") or action_type.startswith("list") or action_type.startswith("set"):
        context.user_data['initial_action'] = action_type

    clicked_button_data = query.data
    user_id = update.effective_user.id

    if clicked_button_data == "back_to_start":
        await start(update, context)

    elif clicked_button_data == "add_flashcard_":
        await handle_list_modules(update, context)

    elif clicked_button_data == "list_flashcards_":
        await handle_list_modules(update, context)

    elif clicked_button_data.startswith("revise_"):
        await handle_list_modules(update, context)

    elif clicked_button_data.startswith("set_"):
        await handle_set_Time(update, context)

    elif clicked_button_data == "add_module":
        context.user_data["add_module"] = "new module"
        await query.edit_message_text("Tapez le nom du module que vous souhaitez ajouter.", reply_markup=back_module_button())
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
    elif clicked_button_data.startswith("modify_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_modify_module(update, context)
   

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
                # 📌 Extraction du chemin de l'image avec regex
                match = re.search(r'\(([^)]+)\)', flashcard['front'])  
                if match:
                    photo_path = match.group(1)  # Récupère le texte entre ()
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=open(photo_path, "rb"),  # 📌 Ouvre et envoie l'image
                        caption=f"<b>Verso :</b> {flashcard['back']}",
                        parse_mode="HTML"
                    )
                else:
                    # 📌 Si aucun chemin d'image trouvé, afficher normalement
                    await query.edit_message_text(
                        f"<b>Recto :</b> {flashcard['front']}\n<b>Verso :</b> {flashcard['back']}",
                        parse_mode="HTML",
                        reply_markup=back_module_button()
                    )
            else:
                await query.edit_message_text("Flashcard introuvable.", reply_markup=back_module_button())



    
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
    elif clicked_button_data.startswith("delete_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_delete_module(update, context)
    elif clicked_button_data.startswith("modify_flashcard_"):
        await handle_modify_flashcard(update,context)
    elif clicked_button_data == "back_to_modules":
        await handle_list_modules(update, context)

    elif clicked_button_data.startswith("module_"):
        await handle_list_cours(update, context)

    elif clicked_button_data.startswith("course_"):
        await handle_click_cours(update, context)

    elif clicked_button_data.startswith("modify_course_"):
        await handle_modify_course(update, context)

    elif clicked_button_data.startswith("add_course_"):
        await handle_add_cours(update, context)

    elif clicked_button_data.startswith("delete_course_"):
        await handle_delete_course(update, context)


    elif clicked_button_data.startswith("delete_flashcard_"):
        await handle_delete_flashcard(update, context)

    elif clicked_button_data.startswith("modify_front"):
        await handle_modify_choice(update, context)

    elif clicked_button_data.startswith("modify_back"):
        await handle_modify_choice(update, context)

    elif clicked_button_data.startswith("modify_both"):
        await handle_modify_choice(update, context)


    elif clicked_button_data.startswith("backListFlashcard_"):
        await handler_list_flashcardupdate(update, context)

    elif clicked_button_data.startswith("next_card_"):
        await handle_next_card(update, context)

    elif clicked_button_data == "restart_revision":
        await handle_restart_revision(update, context)

    elif clicked_button_data.startswith("remembered_") or clicked_button_data.startswith("forgot_"):
        await handle_revision_feedback(update, context)

    elif clicked_button_data == "listModule_":
        await handle_list_modules_set_Time(update, context)

    elif clicked_button_data.startswith("show_back_"):
        await handle_show_back(update, context)

    elif clicked_button_data.startswith("moduletime_"):
        await handle_list_cours_set_time(update, context)

    elif clicked_button_data.startswith("coursetime_"):
        await handler_list_flashcardupdate_set_time(update, context)

    elif clicked_button_data.startswith("show_flashcard_set_time_"):
        await handler_show_flashcard_set_time(update, context)

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

    elif clicked_button_data.startswith("prev_month_") or clicked_button_data.startswith("next_month_"):
        _, _, year, month = clicked_button_data.split("_")
        year = int(year)
        month = int(month)

        if clicked_button_data.startswith("prev_month_"):
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
        elif clicked_button_data.startswith("next_month_"):
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        keyboard = generate_calendar(year, month)
        await query.edit_message_text(
            f"📅 Calendrier pour {calendar.month_name[month]} {year} :",
            reply_markup=keyboard
        )

    elif clicked_button_data.startswith("start_revision_"):
        await start_revision_callback(update, context)

    elif clicked_button_data.startswith("select_moduleSETREVISION_"):
        await select_module_callback(update, context)

    elif clicked_button_data.startswith("start_course_revision_"):
        await start_course_revision(update, context)

    elif clicked_button_data.startswith("show_answer_"):
        await show_answer_callback(update, context)

    elif clicked_button_data.startswith("next_card_setTime_"):
        await next_flashcard_callback(update, context)
    elif query.data == "add_text":
        await query.edit_message_text("Veuillez saisir le <b>recto</b> de la carte mémoire.", reply_markup=back_cours_button(), parse_mode="HTML")
    elif query.data == "add_photo":
        await query.edit_message_text("Veuillez envoyer une photo pour le <b>recto</b> de la carte mémoire.", reply_markup=back_cours_button(), parse_mode="HTML")

    
def extract_callback_data(callback_data):
    parts = callback_data.split("_")
    action_type = parts[0]
    params = parts[1:]
    return action_type, params

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Error: {context.error}")
    if update and update.effective_chat:
        await update.effective_chat.send_message(f"Une erreur est survenue: {context.error}")

async def handle_photo(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()

    if not os.path.exists('photos'):
        os.makedirs('photos')

    file_path = f"photos/{file.file_id}.jpg"
    await file.download_to_drive(file_path)

    # Stocker temporairement l'image et demander un titre
    context.user_data["pending_image"] = file_path
    await update.message.reply_text("Veuillez entrer un titre pour cette image 📌")
