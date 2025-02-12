from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
from data.storage import get_due_flashcards, get_flashcards

async def handler_revise_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    parts = clicked_button_data.split("_")
    print("heree")
    print(parts)
    if len(parts) == 3:  # Format: "revise_moduleName_courseName"
        print("here2")
        _, module_name, course_name = parts
        due_flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch due flashcards

        if not due_flashcards:
            print("here3")
            keyboard = []
            keyboard.append([InlineKeyboardButton("Back", callback_data=f"course_{module_name}_{course_name}")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text("No flashcards due for revision.", reply_markup=reply_markup)
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

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Revision session completed!\nYou got {score}/{total_flashcards} right.",
            reply_markup=reply_markup
        )
        return

    flashcard = flashcards[current_index]
    keyboard = [
        [InlineKeyboardButton("Show Back", callback_data=f"show_back_{current_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if flashcard['front'].startswith('photos/'):
        # Send the photo
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(flashcard['front'], 'rb'), caption=f"Flashcard {current_index + 1}/{len(flashcards)}", reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Flashcard {current_index + 1}/{len(flashcards)}\nFront: {flashcard['front']}",
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

        if flashcard['front'].startswith('photos/'):
            # Send the photo
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(flashcard['front'], 'rb'), caption=f"Front: {flashcard['front']}\nBack: {flashcard['back']}\nDid you remember?", reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Front: {flashcard['front']}\nBack: {flashcard['back']}\nDid you remember?",
                reply_markup=reply_markup
            )

async def handle_revision_feedback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    print("parts for handle remembered and forgot ", parts)
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

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Revision session completed!\nYou got {score}/{total_flashcards} right.",
                reply_markup=reply_markup
            )
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
            keyboard = []
            keyboard.append([InlineKeyboardButton("Back", callback_data=f"course_{module_name}_{course_name}")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text("Could not restart revision. Please start a new session.", reply_markup=reply_markup)
        return

    # Restart the revision session with existing data
    revision_state["current_index"] = 0
    revision_state["score"] = 0
    random.shuffle(revision_state["flashcards"])  # Shuffle again for randomness
    await show_next_flashcard(update, context)
