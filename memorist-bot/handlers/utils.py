from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.storage import get_courses, get_flashcards, add_flashcard, get_modules ,update_flashcard_review,get_due_flashcards # Import get_modules

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    
    if clicked_button_data == "add_module":
        # Handle "Add Module" button
        await query.edit_message_text("Type the name of the module you want to add.", reply_markup=get_back_button())
    elif clicked_button_data == "back_to_modules":
        # Handle "Back" button to return to the list of modules
        modules = get_modules()
        
        # Create a list of buttons for each module
        keyboard = [
            [InlineKeyboardButton(module, callback_data=f"module_{module}")] for module in modules
        ]
        
        # Add an "Add Module" button
        keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("Your modules:", reply_markup=reply_markup)
    elif clicked_button_data.startswith("module_"):
        # Handle module button clicks
        module_name = clicked_button_data.replace("module_", "")
        courses = get_courses(module_name)
        
        # Create a list of buttons for each course
        keyboard = [
            [InlineKeyboardButton(course, callback_data=f"course_{module_name}_{course}")] for course in courses
        ]
        
        # Add an "Add Course" button
        keyboard.append([InlineKeyboardButton("Add Course", callback_data=f"add_course_{module_name}")])
        
        # Add a "Back" button
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_modules")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(f"Courses for module '{module_name}':", reply_markup=reply_markup)
    elif clicked_button_data.startswith("course_"):
        # Handle course button clicks
        parts = clicked_button_data.split("_")
        if len(parts) == 3:  # Format: "course_moduleName_courseName"
            _, module_name, course_name = parts
            
            # Create buttons for flashcard actions
            keyboard = [
                [InlineKeyboardButton("Add Flashcard", callback_data=f"add_flashcard_{module_name}_{course_name}")],
                [InlineKeyboardButton("List Flashcards", callback_data=f"list_flashcards_{module_name}_{course_name}")],
                [InlineKeyboardButton("Revise", callback_data=f"revise_{module_name}_{course_name}")],
                [InlineKeyboardButton("Back", callback_data=f"module_{module_name}")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(f"Course: {course_name}\nWhat would you like to do?", reply_markup=reply_markup)

    elif clicked_button_data.startswith("add_flashcard_"):
        # Handle "Add Flashcard" button clicks
        parts = clicked_button_data.split("_")
        if len(parts) == 4:  # Format: "add_flashcard_moduleName_courseName"
            _, _, module_name, course_name = parts
            context.user_data["flashcard_state"] = {
                "module": module_name,
                "course": course_name,
                "step": "front"  # First step: ask for the front of the flashcard
            }
            await query.edit_message_text("Please type the **front** of the flashcard.", reply_markup=get_back_button())

    elif clicked_button_data.startswith("revise_"):
        # Handle "Revise" button clicks
        await query.edit_message_text("Coming soon!", reply_markup=get_back_button())

    elif clicked_button_data.startswith("add_course_"):
        # Handle "Add Course" button clicks
        module_name = clicked_button_data.replace("add_course_", "")
        context.user_data["current_module"] = module_name  # Store the current module in user_data
        await query.edit_message_text(f"Type the name of the course you want to add to module '{module_name}'.", reply_markup=get_back_button())

    elif clicked_button_data.startswith("list_flashcards_"):
        # Handle "List Flashcards" button clicks
        parts = clicked_button_data.split("_")
        if len(parts) == 4:  # Format: "list_flashcards_moduleName_courseName"
            _, _, module_name, course_name = parts
            flashcards = get_flashcards(module_name, course_name)
            
            if not flashcards:
                await query.edit_message_text("No flashcards found for this course.", reply_markup=get_back_button())
            else:
                # Create a list of buttons for each flashcard (front only)
                keyboard = [
                    [InlineKeyboardButton(flashcard["front"], callback_data=f"show_flashcard_{module_name}_{course_name}_{index}")]
                    for index, flashcard in enumerate(flashcards)
                ]
                
                # Add a "Back" button
                keyboard.append([InlineKeyboardButton("Back", callback_data=f"course_{module_name}_{course_name}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text("Flashcards (click to reveal the back):", reply_markup=reply_markup)

    elif clicked_button_data.startswith("show_flashcard_"):
        # Handle flashcard button clicks (reveal the back)
        parts = clicked_button_data.split("_")
        if len(parts) == 5:  # Format: "show_flashcard_moduleName_courseName_index"
            _, _, module_name, course_name, index = parts
            flashcards = get_flashcards(module_name, course_name)
            flashcard = flashcards[int(index)]
            
            await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}", reply_markup=get_back_button())    



async def show_next_flashcard(update: Update, context: CallbackContext) -> None:
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    flashcards = revision_state["flashcards"]
    current_index = revision_state["current_index"]
    
    if current_index >= len(flashcards):
        # End of revision session
        await update.callback_query.edit_message_text("Revision session completed!", reply_markup=get_back_button())
        del context.user_data["revision_state"]
        return
    
    flashcard = flashcards[current_index]
    keyboard = [
        [InlineKeyboardButton("Reveal Answer", callback_data=f"reveal_answer_{current_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(f"Flashcard {current_index + 1}/{len(flashcards)}\nFront: {flashcard['front']}", reply_markup=reply_markup)

async def handle_reveal_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    flashcards = revision_state["flashcards"]
    current_index = revision_state["current_index"]
    flashcard = flashcards[current_index]
    
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f"remembered_{current_index}")],
        [InlineKeyboardButton("No", callback_data=f"forgot_{current_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}\nDid you remember?", reply_markup=reply_markup)

async def handle_revision_feedback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 2:  # Format: "remembered_index" or "forgot_index"
        feedback, index = parts
        revision_state = context.user_data.get("revision_state")
        if not revision_state:
            return
        
        module_name = revision_state["module"]
        course_name = revision_state["course"]
        flashcard_index = int(index)
        
        # Update the flashcard's review interval
        update_flashcard_review(module_name, course_name, flashcard_index, feedback == "remembered")
        
        # Move to the next flashcard
        revision_state["current_index"] += 1
        await show_next_flashcard(update, context)

def get_back_button():
    # Helper function to create a "Back" button
    keyboard = [[InlineKeyboardButton("Back", callback_data="back_to_modules")]]
    return InlineKeyboardMarkup(keyboard)