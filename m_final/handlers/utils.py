from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext , ContextTypes
import random
from .module import *
from .cours import handle_list_cours,handle_delete_course,handle_modify_course,handle_add_cours,handle_click_cours
from .revision import *
from .set_revision import *
from .backBTN import *
from .start import start
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review,delete_module , delete_cours,delete_flashcard_by_id
)

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    action_type, params = extract_callback_data(query.data)
    if action_type.startswith("add") or action_type.startswith("revise") or action_type.startswith("list") or action_type.startswith("set"):
        context.user_data['initial_action'] = action_type
    # # Stocker l'action initiale si ce n'est pas déjà fait
    # if 'initial_action' not in context.user_data:
    #     context.user_data['initial_action'] = action_type
    print("initial action", context.user_data['initial_action'])
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    user_id = update.effective_user.id  # Get the user ID
    callback_data = query.data

    if clicked_button_data == "add_module":
        # Handle "Add Module" button
        await query.edit_message_text("Type the name of the module you want to add.", reply_markup=back_module_button())

    elif clicked_button_data.startswith("modify_module_"):
        # Extract module name from callback data
        module_name = clicked_button_data.replace("module_", "")
        await handle_modify_module(update,context)

    elif clicked_button_data.startswith("delete_module_"):
        module_name = clicked_button_data.replace("module_", "")
        await handle_delete_module(update,context)

    elif clicked_button_data == "back_to_modules":
        await handle_list_modules(update,context)
       
    elif clicked_button_data.startswith("module_"):
        await handle_list_cours(update,context)
    
    elif clicked_button_data.startswith("moduletime_"): # print courses for set time 
        await handle_list_cours_set_time(update,context)
    
    elif clicked_button_data.startswith("coursetime_"): # print flashcards for set time 
        await handler_list_flashcardupdate_set_time(update,context)

    elif clicked_button_data.startswith("show_flashcard_set_time_"):
        await handler_show_flashcard_set_time(update,context)


    elif clicked_button_data.startswith("course_"):
        await handle_click_cours(update,context)

    elif clicked_button_data.startswith("modify_course_"):
        await handle_modify_course(update,context)

    elif clicked_button_data.startswith("add_course_"):
        await handle_add_cours(update,context)
        
    elif clicked_button_data.startswith("delete_course_"):
        await handle_delete_course(update,context)
    elif clicked_button_data =="back_to_start":
        await start(update,context)
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
    # for the start button------------------------------------------------------------------------------------
    elif clicked_button_data == "add_flashcard_":
        await handle_list_modules(update,context)

    elif clicked_button_data == "list_flashcards_":
        await handle_list_modules(update,context)

    elif clicked_button_data.startswith("revise_"):
        # Handle "Revise" button clicks
        await handle_list_modules(update,context)
    elif clicked_button_data.startswith("set_"):
        await handle_set_Time(update,context)
    
    elif clicked_button_data==("listModule_"): # definir une heure de revision pour les modules 
        await  handle_list_modules_set_Time(update,context)
    # elif clicked_button_data.startswith("revise_"):
    #     # Handle "Revise" button clicks
    #     print("here1")
        # parts = clicked_button_data.split("_")
        # print("heree")
        # print(parts)
        # if len(parts) == 3:  # Format: "revise_moduleName_courseName"
        #     print("here2")
        #     _, module_name, course_name = parts
        #     due_flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch due flashcards
            
        #     if not due_flashcards:
        #         print("here3")
        #         await query.edit_message_text("No flashcards due for revision.", reply_markup=get_back_button())
        #     else:
        #         print("here")
        #         # Shuffle flashcards for random order
        #         random.shuffle(due_flashcards)
                
        #         # Start the revision session
        #         context.user_data["revision_state"] = {
        #             "module": module_name,
        #             "course": course_name,
        #             "flashcards": due_flashcards,
        #             "current_index": 0,
        #             "score": 0  # Initialize score
        #         }
        #         await show_next_flashcard(update, context)

    elif clicked_button_data.startswith("show_back_"):  # Call handle_show_back when "Show Back" is clicked
        await handle_show_back(update, context)
    elif clicked_button_data.startswith("next_card_"):
        await handle_next_card(update, context)
    elif clicked_button_data == "restart_revision":
        print("restart r")
        await handle_restart_revision(update, context)
    elif clicked_button_data.startswith("remembered_") or clicked_button_data.startswith("forgot_"):
        await handle_revision_feedback(update, context)
        
    # elif clicked_button_data.startswith("show_flashcard_"):
    #     # Handle flashcard button clicks (reveal the back)
    #     parts = clicked_button_data.split("_")
    #     print("show flashcard list  parts",parts)
    #     if len(parts) == 3:  # Format: "show_flashcard_moduleName_courseName_flashcardId"
    #         _, _, flashcard_id = parts
    #         # flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch flashcards for the course
    #         module_name = context.user_data.get('module_name')
    #         course_name = context.user_data.get('course_name')
    #         flashcard = next((f for f in flashcards if f["id"] == int(flashcard_id)), None)
            
    #         if flashcard:
    #             await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}", reply_markup=get_back_button())
    #         else:
    #             await query.edit_message_text("Flashcard not found.", reply_markup=get_back_button())
    elif clicked_button_data.startswith("show_flashcard_"):
        # Gérer les clics de bouton flashcard (révéler le verso)
        parts = clicked_button_data.split("_")
        print("show flashcard list parts", parts)

        if len(parts) == 3:  # Format: "show_flashcard_flashcardId"
            _, _, flashcard_id = parts

            # Récupérer les informations du module et du cours depuis context.user_data
            module_name = context.user_data.get('module_name')
            course_name = context.user_data.get('course_name')

            if not module_name or not course_name:
                await query.edit_message_text("Erreur : Module ou cours non spécifié.")
                return

            user_id = update.effective_user.id
            # Récupérer toutes les flashcards du storage
            all_flashcards = get_flashcards(module_name, course_name, user_id)

            # Rechercher la flashcard avec l'ID correspondant
            flashcard = next((f for f in all_flashcards if str(f['id']) == flashcard_id), None)


            if flashcard:
                await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}", reply_markup=back_module_button())
            else:
                await query.edit_message_text("Flashcard not found.", reply_markup=back_module_button())
    
    elif clicked_button_data.startswith("modify_flashcard_"):
        await handle_modify_flashcard(update,context)
    elif clicked_button_data.startswith("delete_flashcard_"):
        await handle_delete_flashcard(update,context)
    elif clicked_button_data.startswith("modify_front"):
        await handle_modify_choice(update,context)
    elif clicked_button_data.startswith("modify_back"):
        await handle_modify_choice(update,context)
    elif clicked_button_data.startswith("modify_both"):
        await handle_modify_choice(update,context)


   





async def handle_delete_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "delete_flashcard_flashcardId"
        flashcard_id = int(parts[2])
        delete_flashcard_by_id(flashcard_id)
        await query.edit_message_text("Flashcard deleted!", reply_markup=back_module_button())


async def handle_modify_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    print("parts for flashcard",parts)
    if len(parts) == 3:  # Format: "modify_flashcard_flashcardId"
        flashcard_id = int(parts[2])
        context.user_data["modify_flashcard"] = {
            "id": flashcard_id,
            "step": "choose_field"
        }
        
        # Ask user what to modify
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
    
    choice = query.data  # "modify_front", "modify_back", or "modify_both"
    print("context user data : ",context.user_data)
    context.user_data["modify_flashcard"]["choice"] = choice
    
    if choice == "modify_front":
        await query.edit_message_text("Enter the new FRONT text:")
    elif choice == "modify_back":
        await query.edit_message_text("Enter the new BACK text:")
    elif choice == "modify_both":
        await query.edit_message_text("Enter the new FRONT text first:")
    elif choice =="back_to_course_{context.user_data.get('current_course')}":
        return






def extract_callback_data(callback_data):
    """Extrait le type d'action et les paramètres du callback_data."""
    parts = callback_data.split("_")
    action_type = parts[0]  # Par exemple, "add", "revise", "list"
    params = parts[1:]       # Le reste des parties, si applicable
    return action_type, params



async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # ... (Your error handling logic here) ...
    print(f"Error: {context.error}")
    if update and update.effective_chat:
        await update.effective_chat.send_message(f"An error occurred: {context.error}")


