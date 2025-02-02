from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
from data.storage import (
    add_module, get_modules, add_course, get_courses,
    add_flashcard, get_flashcards, get_due_flashcards, update_flashcard_review,delete_module
)

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    user_id = update.effective_user.id  # Get the user ID
    callback_data = query.data

    if clicked_button_data == "add_module":
        # Handle "Add Module" button
        await query.edit_message_text("Type the name of the module you want to add.", reply_markup=get_back_button())

    elif clicked_button_data.startswith("modify_module_"):
        print("and here?")
        #  # Extract module name from callback data
        module_name = clicked_button_data.replace("module_", "")
        print("modify?")
        await handle_modify_module(update,context)
    elif clicked_button_data.startswith("delete_module_"):
        print("and here?")
        #  # Extract module name from callback data
        module_name = clicked_button_data.replace("module_", "")
        print("modify?")
        await handle_delete_module(update,context)

    elif clicked_button_data == "back_to_modules":
        # Handle "Back" button to return to the list of modules
        modules = get_modules(user_id)  # Fetch modules for the current user
        
        # Create a list of buttons for each module
        keyboard = [
            [InlineKeyboardButton(module, callback_data=f"module_{module}")] for module in modules
        ]
        
        # Add an "Add Module" button
        keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("Your modules:", reply_markup=reply_markup)
    
    elif clicked_button_data.startswith("module_"):
        #  # Extract module name from callback data
        module_name = clicked_button_data.replace("module_", "")
        
  
        
        courses = get_courses(module_name, user_id)  # Fetch courses for the module and user
        
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
        print("add f",parts)
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
        print("here1")
        parts = clicked_button_data.split("_")
        print("heree")
        print(parts)
        if len(parts) == 3:  # Format: "revise_moduleName_courseName"
            print("here2")
            _, module_name, course_name = parts
            due_flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch due flashcards
            
            if not due_flashcards:
                print("here3")
                await query.edit_message_text("No flashcards due for revision.", reply_markup=get_back_button())
            else:
                print("here")
                # Shuffle flashcards for random order
                random.shuffle(due_flashcards)
                
                # Start the revision session
                context.user_data["revision_state"] = {
                    "module": module_name,
                    "course": course_name,
                    "flashcards": due_flashcards,
                    "current_index": 0,
                    "score": 0  # Initialize score
                }
                await show_next_flashcard(update, context)

    elif clicked_button_data.startswith("show_back_"):  # Call handle_show_back when "Show Back" is clicked
        await handle_show_back(update, context)
    elif clicked_button_data.startswith("next_card_"):
        await handle_next_card(update, context)
    elif clicked_button_data == "restart_revision":
        print("restart r")
        await handle_restart_revision(update, context)
    elif clicked_button_data.startswith("remembered_") or clicked_button_data.startswith("forgot_"):
        await handle_revision_feedback(update, context)
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
            flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch flashcards for the course
            
            if not flashcards:
                await query.edit_message_text("No flashcards found for this course.", reply_markup=get_back_button())
            else:
                # Create a list of buttons for each flashcard (front only)
                keyboard = [
                    [InlineKeyboardButton(flashcard["front"], callback_data=f"show_flashcard_{module_name}_{course_name}_{flashcard['id']}")]
                    for flashcard in flashcards
                ]
                
                # Add a "Back" button
                keyboard.append([InlineKeyboardButton("Back", callback_data=f"course_{module_name}_{course_name}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text("Flashcards (click to reveal the back):", reply_markup=reply_markup)
    
    elif clicked_button_data.startswith("show_flashcard_"):
        # Handle flashcard button clicks (reveal the back)
        parts = clicked_button_data.split("_")
        if len(parts) == 5:  # Format: "show_flashcard_moduleName_courseName_flashcardId"
            _, _, module_name, course_name, flashcard_id = parts
            flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch flashcards for the course
            flashcard = next((f for f in flashcards if f["id"] == int(flashcard_id)), None)
            
            if flashcard:
                await query.edit_message_text(f"Front: {flashcard['front']}\nBack: {flashcard['back']}", reply_markup=get_back_button())
            else:
                await query.edit_message_text("Flashcard not found.", reply_markup=get_back_button())




async def show_next_flashcard(update: Update, context: CallbackContext) -> None:
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    flashcards = revision_state["flashcards"]
    current_index = revision_state["current_index"]
    
    if current_index >= len(flashcards):
        # End of revision session
        score = revision_state["score"]
        total_flashcards = len(flashcards)
        
        # Create keyboard with "Restart Revision" and "Back" buttons
        keyboard = [
            [InlineKeyboardButton("Restart Revision", callback_data="restart_revision")],
            [InlineKeyboardButton("Back", callback_data="back_to_modules")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"Revision session completed!\nYou got {score}/{total_flashcards} right.",
            reply_markup=reply_markup
        )
        # del context.user_data["revision_state"]
        return
    
    flashcard = flashcards[current_index]
    keyboard = [
        [InlineKeyboardButton("Show Back", callback_data=f"show_back_{current_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"Flashcard {current_index + 1}/{len(flashcards)}\nFront: {flashcard['front']}",
        reply_markup=reply_markup
    )

async def handle_show_back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "show_back_index"
        current_index = int(parts[2])
        flashcard = revision_state["flashcards"][current_index]
        
        # Create buttons for feedback
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data=f"remembered_{current_index}")],
            [InlineKeyboardButton("No", callback_data=f"forgot_{current_index}")]
        ]
        
        # If it's the last flashcard, add "Restart Revision" button
        if current_index == len(revision_state["flashcards"]) - 1:
            keyboard.append([InlineKeyboardButton("Restart Revision", callback_data="restart_revision")])
        else:
            keyboard.append([InlineKeyboardButton("Next Card", callback_data=f"next_card_{current_index}")])
        
        # Add a "Back" button
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_modules")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Front: {flashcard['front']}\nBack: {flashcard['back']}\nDid you remember?",
            reply_markup=reply_markup
        )

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
        
        # Update the score
        if feedback == "remembered":
            revision_state["score"] += 1
        # else:
        #     revision_state["score"] -= 0
        
        # Move to the next flashcard
        revision_state["current_index"] += 1
        
        # If it's the last flashcard, end the session and show the score
        if revision_state["current_index"] >= len(revision_state["flashcards"]):
            score = revision_state["score"]
            total_flashcards = len(revision_state["flashcards"])
            
            # Create keyboard with "Restart Revision" and "Back" buttons
            keyboard = [
                [InlineKeyboardButton("Restart Revision", callback_data="restart_revision")],
                [InlineKeyboardButton("Back", callback_data="back_to_modules")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Revision session completed!\nYou got {score}/{total_flashcards} right.",
                reply_markup=reply_markup
            )
            # del context.user_data["revision_state"]
        else:
            await show_next_flashcard(update, context)


async def handle_next_card(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    # Move to the next flashcard
    revision_state["current_index"] += 1
    await show_next_flashcard(update, context)

async def handle_restart_revision(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        # If revision_state is missing, try to recreate it
        module_name = context.user_data.get("revision_module")
        course_name = context.user_data.get("revision_course")
        user_id = update.effective_user.id
        
        if module_name and course_name:
            due_flashcards = get_due_flashcards(module_name, course_name, user_id)
            random.shuffle(due_flashcards)
            
            context.user_data["revision_state"] = {
                "module": module_name,
                "course": course_name,
                "flashcards": due_flashcards,
                "current_index": 0,
                "score": 0
            }
            await show_next_flashcard(update, context)
        else:
            await query.edit_message_text("Could not restart revision. Please start a new session.", reply_markup=get_back_button())
        return
    
    # Restart the revision session with existing data
    revision_state["current_index"] = 0
    revision_state["score"] = 0
    random.shuffle(revision_state["flashcards"])  # Shuffle again for randomness
    await show_next_flashcard(update, context)

   

async def handle_modify_module(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "modify_module_moduleName"
        _, _, module_name = parts
        context.user_data["modify_module"] = module_name
        await query.edit_message_text(f"Enter the new name for module '{module_name}':", reply_markup=get_back_button())


async def handle_delete_module(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "delete_module_moduleName"
        _, _, module_name = parts
        user_id = update.effective_user.id

        # Delete the module and its associated courses and flashcards
        delete_module(module_name, user_id)
        await query.edit_message_text(f"Module '{module_name}' and all its courses/flashcards have been deleted.", reply_markup=get_back_button())









def get_back_button():
    # Helper function to create a "Back" button
    keyboard = [[InlineKeyboardButton("Back", callback_data="back_to_modules")]]
    return InlineKeyboardMarkup(keyboard)