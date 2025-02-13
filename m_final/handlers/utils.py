from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext , ContextTypes
import random
from .module import *
from .cours import handle_list_cours,handle_delete_course,handle_modify_course,handle_add_cours,handle_click_cours
from .revision import *
from .set_revision import *
from .backBTN import *
from .start import start
from .flashcard import handle_delete_flashcard, handle_modify_choice, handle_modify_flashcard,handle_show_flashcard, handler_list_flashcardupdate
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review,delete_module , delete_cours,delete_flashcard_by_id
)
from .set_revision_f.start_revision import *

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    action_type, params = extract_callback_data(query.data)

    # initialisation 
    if action_type.startswith("add") or action_type.startswith("revise") or action_type.startswith("list") or action_type.startswith("set"):
        context.user_data['initial_action'] = action_type
    # # Stocker l'action initiale si ce n'est pas déjà fait
    print("initial action", context.user_data['initial_action'])
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    user_id = update.effective_user.id  # Get the user ID
    callback_data = query.data

    # action :
    # retour au menu de start
    if clicked_button_data =="back_to_start":
        await start(update,context)

    # 4 start buttons : 
    # boutton1: ajouter flash card
    elif clicked_button_data == "add_flashcard_":
        await handle_list_modules(update,context)

    # boutton2 : liste flashcard
    elif clicked_button_data == "list_flashcards_":
        await handle_list_modules(update,context)

    # boutton3: reviser
    elif clicked_button_data.startswith("revise_"):
        await handle_list_modules(update,context)

    #boutton4: set time revision  
    elif clicked_button_data.startswith("set_"):
        await handle_set_Time(update,context)

    # ajouter un module
    elif clicked_button_data == "add_module":
        # Handle "Add Module" button
        context.user_data["add_module"] = "new module"
        await query.edit_message_text("Type the name of the module you want to add.", reply_markup=back_module_button())

    #modifier un module
    elif clicked_button_data.startswith("modify_module_"):
        # Extract module name from callback data
        module_name = clicked_button_data.replace("module_", "")
        await handle_modify_module(update,context)

    # supprimer un module 
    elif clicked_button_data.startswith("delete_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_delete_module(update,context)

    # retour à la liste des modules 
    elif clicked_button_data == "back_to_modules":
        await handle_list_modules(update,context)

    # retour à la liste des cours 
    # elif clicked_button_data.startswith("back_to_courses"):
    #     await handle_list_cours(update,context)

    # afficher la liste des cours du module "m"   -- aussi utiliser pour le boutton "retour" afin de retourner a la liste des cours
    elif clicked_button_data.startswith("module_"):
        await handle_list_cours(update,context)
    
    elif clicked_button_data.startswith("course_"):
        await handle_click_cours(update,context)

    # modifier le nom du cours 
    elif clicked_button_data.startswith("modify_course_"):
        await handle_modify_course(update,context)

    # ajouter un cours
    elif clicked_button_data.startswith("add_course_"):
        await handle_add_cours(update,context)
    
    # supprimer un cours 
    elif clicked_button_data.startswith("delete_course_"):
        await handle_delete_course(update,context)
    
    # modifier une carte 
    elif clicked_button_data.startswith("modify_flashcard_"):
        await handle_modify_flashcard(update,context)

    # supprimer une carte 
    elif clicked_button_data.startswith("delete_flashcard_"):
        await handle_delete_flashcard(update,context)

    # modifier uniquement le front de la carte
    elif clicked_button_data.startswith("modify_front"):
        await handle_modify_choice(update,context)

    # mdofier uniquement le back de la carte 
    elif clicked_button_data.startswith("modify_back"):
        await handle_modify_choice(update,context)

    # modifier le front & le back de la carte
    elif clicked_button_data.startswith("modify_both"):
        await handle_modify_choice(update,context)
    
    # afficher flashcard (front & back)
    elif clicked_button_data.startswith("show_flashcard_"):
        await handle_show_flashcard(update,context)

    # retrour à la liste des carte
    elif clicked_button_data.startswith("backListFlashcard_"):
        await handler_list_flashcardupdate(update,context)
        



    
    elif clicked_button_data.startswith("next_card_"):
        await handle_next_card(update, context)
    elif clicked_button_data == "restart_revision":
        print("restart r")
        await handle_restart_revision(update, context)
    elif clicked_button_data.startswith("remembered_") or clicked_button_data.startswith("forgot_"):
        await handle_revision_feedback(update, context)
        
    
    
    # SET TIME REVISION -------------------------------------------
    elif clicked_button_data==("listModule_"): # definir une heure de revision pour les modules 
        await  handle_list_modules_set_Time(update,context)
    
    elif clicked_button_data.startswith("show_back_"):  # Call handle_show_back when "Show Back" is clicked
        await handle_show_back(update, context)
    
    elif clicked_button_data.startswith("moduletime_"): # print courses for set time 
        await handle_list_cours_set_time(update,context)
    
    elif clicked_button_data.startswith("coursetime_"): # print flashcards for set time 
        await handler_list_flashcardupdate_set_time(update,context)

    elif clicked_button_data.startswith("show_flashcard_set_time_"):
        await handler_show_flashcard_set_time(update,context)


    elif clicked_button_data.startswith("definir_time_module_"):
        await handle_set_time_module(update,context)
    elif clicked_button_data.startswith("definir_time_cours_"):
        await handle_set_time_course(update,context)
    elif clicked_button_data.startswith("definir_time_flashcard_"):
        await handle_set_time_flashcard(update,context)

    elif clicked_button_data.startswith("select_day_"):
        await select_day(update,context)
    elif clicked_button_data.startswith("selected_date_"):
        await handle_time_input(update,context)
    elif clicked_button_data=="confirm_schedule":
        await confirm_schedule(update,context)
    elif clicked_button_data.startswith("add_hour_"):
        await add_hour(update,context)
    elif clicked_button_data=="palnning":
        await handle_planning_set_time(update,context)
    elif clicked_button_data=="confirm_hour":
        await confirm_hour(update,context)
    # START REVISION POUR SET TIME ------------------------------------------------------------
    elif clicked_button_data.startswith("prev_month_") or clicked_button_data.startswith("next_month_"):
        print("calander parts",clicked_button_data.split("_"))
        # Extraire l'année et le mois actuels
        _,_, year, month = clicked_button_data.split("_")
        year = int(year)
        month = int(month)

        # Calculer le mois précédent ou suivant
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

        # Générer le nouveau calendrier
        keyboard = generate_calendar(year, month)
        await query.edit_message_text(
            f"📅 Calendrier pour {calendar.month_name[month]} {year} :",
            reply_markup=keyboard
        )

    elif clicked_button_data.startswith("start_revision_"): #commencer la revision pour set time revision 
        await start_revision_callback(update,context)
    elif clicked_button_data.startswith("select_moduleSETREVISION_"): #selectionner le module de set time revision
        await select_module_callback(update,context)
    elif clicked_button_data.startswith("start_course_revision_"):
        await start_course_revision(update,context)
    elif clicked_button_data.startswith("show_answer_"):
        await show_answer_callback(update,context)
    elif clicked_button_data.startswith("next_card_setTime_"):
        await next_flashcard_callback(update,context)


    # fEND SET TIME ------------------------------------------------------------------------------------
    

   



# pour stocker le boutton initial ( add , set , revise , list )
def extract_callback_data(callback_data):
    """Extrait le type d'action et les paramètres du callback_data."""
    parts = callback_data.split("_")
    action_type = parts[0]  # Par exemple, "add", "revise", "list"
    params = parts[1:]       # Le reste des parties, si applicable
    return action_type, params


# cas d'erreur
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # ... (Your error handling logic here) ...
    print(f"Error: {context.error}")
    if update and update.effective_chat:
        await update.effective_chat.send_message(f"An error occurred: {context.error}")


