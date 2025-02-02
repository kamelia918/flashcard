# #This file will initialize the bot and register all handlers.


from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler,CallbackContext
from handlers.start import start
from handlers.utils import handle_button_click, get_back_button, handle_reveal_answer, handle_revision_feedback
from data.storage import add_course, add_module, add_flashcard

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    if "current_module" in context.user_data:
        # User is adding a course to a module
        module_name = context.user_data["current_module"]
        add_course(module_name, text)
        await update.message.reply_text(f"Course '{text}' added to module '{module_name}'!", reply_markup=get_back_button())
        del context.user_data["current_module"]  # Clear the current module
    elif "flashcard_state" in context.user_data:
        # User is adding a flashcard
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]
        
        if flashcard_state["step"] == "front":
            # Save the front of the flashcard
            context.user_data["flashcard_state"]["front"] = text
            context.user_data["flashcard_state"]["step"] = "back"  # Move to the next step
            await update.message.reply_text("Now type the **back** of the flashcard.", reply_markup=get_back_button())
        elif flashcard_state["step"] == "back":
            # Save the back of the flashcard
            front = context.user_data["flashcard_state"]["front"]
            back = text
            add_flashcard(module_name, course_name, front, back)
            await update.message.reply_text(f"Flashcard added!\nFront: {front}\nBack: {back}", reply_markup=get_back_button())
            del context.user_data["flashcard_state"]  # Clear the flashcard state
    else:
        # User is adding a module
        add_module(text)
        await update.message.reply_text(f"Module '{text}' added!", reply_markup=get_back_button())

def main() -> None:
    print("Starting bot...")  # Debugging log

    application = Application.builder().token("7758636605:AAE3iDboYqy-5FSH2iXwUgF4_YlvkVKpBGo").build()
    
    print("Bot initialized. Adding handlers...")  # Debugging log

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle modules, courses, and flashcards
    application.add_handler(CallbackQueryHandler(handle_button_click))  # Handle button clicks
    application.add_handler(CallbackQueryHandler(handle_reveal_answer, pattern="^reveal_answer_"))  # Handle reveal answer
    application.add_handler(CallbackQueryHandler(handle_revision_feedback, pattern="^(remembered|forgot)_"))  # Handle revision feedback

    # Start the bot
    print("Bot is running...")
    print("All handlers added. Running polling...")  # Debugging log
    application.run_polling()

if __name__ == "__main__":
    main()