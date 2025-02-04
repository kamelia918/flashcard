from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.storage import delete_cours, get_courses
from .flashcard import handler_add_flashcardupdate,handler_list_flashcardupdate
from .revision import handler_revise_flashcardupdate

async def handle_list_cours(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    user_id = update.effective_user.id

    print("last button",context.user_data['initial_action'] )

    # Extract module name from callback data
    parts = clicked_button_data.split("_")
    if len(parts) == 2:  # Format: "module_moduleName"
        _, module_name = parts
    else:
        # Handle invalid callback_data format
        await query.edit_message_text("Invalid format for listing courses.")
        return

    # Fetch courses for the module
    courses = get_courses(module_name, user_id)

    # Create a list of buttons for each course
    keyboard = []
    for course in courses:
        keyboard.append([
            InlineKeyboardButton(course, callback_data=f"course_{module_name}_{course}"),
            InlineKeyboardButton("✏️ Modifier", callback_data=f"modify_course_{module_name}_{course}"),
            InlineKeyboardButton("🗑️ Supprimer", callback_data=f"delete_course_{module_name}_{course}")
        ])

    # Add an "Add Course" button
    keyboard.append([InlineKeyboardButton("➕ Ajouter un cours", callback_data=f"add_course_{module_name}")])

    # Add a "Back" button
    keyboard.append([InlineKeyboardButton("🔙 Retour à la liste des modules", callback_data="back_to_modules")])

    # Create the reply markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Display the list of courses or a message if no courses exist
    if courses:
        await query.edit_message_text(
            f"Cours du module <b>'{module_name}'</b>:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await query.edit_message_text(
            f"""Aucun cours dans le module <b>{module_name}</b> ajouté pour l'instant. Cliquez sur <b>Ajouter un cours</b> pour en créer un.""",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )



async def handle_modify_course(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    print("parts for modify course ", parts)

    if len(parts) == 4:  # Format: "modify_course_moduleName_courseName"
        _, _, module_name, course_name = parts
        context.user_data["modify_course"] = {
            "module": module_name,
            "old_name": course_name
        }
        
        # Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Enter the new name for course '{course_name}':",
            reply_markup=reply_markup  # Pass the reply_markup directly, no parentheses
        )
    else:
        await query.edit_message_text("Invalid format for modifying course.")

async def handle_delete_course(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")

    if len(parts) == 4:  # Format: "delete_course_moduleName_courseName"
        _, _, module_name, course_name = parts
        user_id = update.effective_user.id
        
        # Delete the course and its flashcards
        delete_cours(module_name, course_name, user_id)  # Ensure this function is defined
        
        # Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Course '{course_name}' and all its flashcards have been deleted.",
            reply_markup=reply_markup  # Pass the reply_markup directly, no parentheses
        )
    else:
        await query.edit_message_text("Invalid format for deleting course.")


async def handle_add_cours(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    callback_data = query.data  # Get the callback_data of the clicked button

    # Extract module_name from the callback_data
    if callback_data.startswith("add_course_"):
        module_name = callback_data.replace("add_course_", "")
        context.user_data["current_module"] = module_name  # Store the current module in user_data

        # Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)


        await query.edit_message_text(
            f"Type the name of the course you want to add to module '{module_name}'.",
            reply_markup=reply_markup  # Pass the reply_markup here
        )
    else:
        await query.edit_message_text("Invalid format for adding a course.")


async def handle_click_cours(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    callback_data = query.data  # Get the callback_data of the clicked button
    action =context.user_data['initial_action'] 
    # Handle course button clicks
    parts = clicked_button_data.split("_")
    if len(parts) == 3:  # Format: "course_moduleName_courseName"
        _, module_name, course_name = parts
        context.user_data['module_name'] = module_name
        context.user_data['course_name'] = course_name
        print("action",action)
        if(action=="add"):
            print("interring add")
            await handler_add_flashcardupdate(update,context)
            print("notl eaving add ")
        elif(action=="revise"):
            await handler_revise_flashcardupdate(update,context)
        elif(action=="list"):
            print("interring cond list ")
            await handler_list_flashcardupdate(update,context)
            print("leaving list ")
        elif(action =="set"):
            print("set time ")    
            

