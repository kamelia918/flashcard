# #This file will initialize the bot and register all handlers.


from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler,CallbackContext
from handlers.start import start
from handlers.utils import handle_button_click, get_back_button, handle_revision_feedback,handle_show_back,handle_restart_revision,handle_next_card,handle_delete_module,handle_modify_module
from data.storage import add_course, add_module, add_flashcard,get_modules,get_courses,get_module_id,get_flashcards,modify_module

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if "modify_module" in context.user_data:
        # Modify module name
        old_name = context.user_data["modify_module"]
        result = modify_module(old_name, text, user_id)

        if result == "success":
            await update.message.reply_text(f"Module '{old_name}' renamed to '{text}'.", reply_markup=get_back_button())
        elif result == "duplicate_module":
            await update.message.reply_text(f"Module '{text}' already exists.", reply_markup=get_back_button())

        del context.user_data["modify_module"]

    elif "current_module" in context.user_data:
        # Adding a course
        module_name = context.user_data["current_module"]
        module_id = get_module_id(module_name, user_id)

        if not module_name:
            await update.message.reply_text(f"Module '{module_name}' not found.", reply_markup=get_back_button())
            return

        # Adding a module
        cours_name = text
        courses = get_courses(module_name,user_id)  # Fetch all modules for the user

        if cours_name in courses:
            await update.message.reply_text(f"Cours '{cours_name}' already exists.", reply_markup=get_back_button())
            return  # Stop execution to prevent adding a duplicate module

        result = add_course(module_id, text, user_id)
        if result == "success":
            await update.message.reply_text(f"Course '{text}' added to module '{module_name}'!", reply_markup=get_back_button())
        elif result == "duplicate_course":
            await update.message.reply_text(f"Course '{text}' already exists in module '{module_name}'.", reply_markup=get_back_button())
        del context.user_data["current_module"]

    elif "flashcard_state" in context.user_data:
        # Adding a flashcard
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]

        if flashcard_state["step"] == "front":
            context.user_data["flashcard_state"]["front"] = text
            # Check if the flashcard already exists
            # Check if the flashcard with the given front text already exists
            if any(flashcard['front'] == text for flashcard in get_flashcards(module_name, course_name, user_id)):
                await update.message.reply_text(f"Flashcard with front '{text}' already exists in this course.", reply_markup=get_back_button())
                return
            context.user_data["flashcard_state"]["step"] = "back"
            await update.message.reply_text("Now type the **back** of the flashcard.", reply_markup=get_back_button())
        elif flashcard_state["step"] == "back":
            front = context.user_data["flashcard_state"]["front"]
            back = text
            
            result = add_flashcard(module_name, course_name, front, back, user_id)
            if result == "success":
                await update.message.reply_text(f"Flashcard added!\nFront: {front}\nBack: {back}", reply_markup=get_back_button())
            elif result == "duplicate_flashcard":
                await update.message.reply_text(f"Flashcard with front '{front}' already exists in this course.", reply_markup=get_back_button())
            del context.user_data["flashcard_state"]

    else:
        # Adding a module
        module_name = text
        modules = get_modules(user_id)  # Fetch all modules for the user

        if module_name in modules:
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=get_back_button())
            return  # Stop execution to prevent adding a duplicate module

        result = add_module(module_name, user_id)

        if result == "success":
            await update.message.reply_text(f"Module '{module_name}' added!", reply_markup=get_back_button())
        elif result == "duplicate_module":
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=get_back_button())


def main() -> None:
    print("Starting bot...")  # Debugging log

    application = Application.builder().token("7758636605:AAE3iDboYqy-5FSH2iXwUgF4_YlvkVKpBGo").build()
    
    print("Bot initialized. Adding handlers...")  # Debugging log

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle modules, courses, and flashcards
    application.add_handler(CallbackQueryHandler(handle_button_click))  # Handle button clicks
    # application.add_handler(CallbackQueryHandler(handle_reveal_answer, pattern="^reveal_answer_"))  # Handle reveal answer
    application.add_handler(CallbackQueryHandler(handle_revision_feedback, pattern="^(remembered|forgot)_"))  # Handle revision feedback
    application.add_handler(CallbackQueryHandler(handle_show_back, pattern="^show_back_"))
    application.add_handler(CallbackQueryHandler(handle_next_card, pattern="^next_card_"))
    application.add_handler(CallbackQueryHandler(handle_restart_revision, pattern="^restart_revision$"))
    application.add_handler(CallbackQueryHandler(handle_modify_module, pattern="^modify_module_"))
    application.add_handler(CallbackQueryHandler(handle_delete_module, pattern="^delete_module_"))
    # Start the bot
    print("Bot is running...")
    print("All handlers added. Running polling...")  # Debugging log
    application.run_polling()

if __name__ == "__main__":
    main()