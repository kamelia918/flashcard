import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from handlers.start import start, set_commands
from handlers.module import modify_module_main
from handlers.cours import handle_add_cours_main
from handlers.backBTN import back_cours_button, back_module_button
from handlers.set_revision import *
from handlers.utils import handle_button_click, handle_revision_feedback, handle_show_back, handle_restart_revision, handle_next_card, handle_delete_module, handle_modify_module, handle_delete_course, handle_modify_course, handle_delete_flashcard, handle_modify_flashcard, handle_modify_choice, error_handler, handle_photo
from data.storage import add_course, add_module, add_flashcard, get_modules, get_courses, get_module_id, get_flashcards, modify_module, modify_cours, modify_flashcard
from handlers.set_revision_f.send_notif import *

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if "modify_module" in context.user_data:
        await modify_module_main(user_id, text, update, context)
    elif "current_module" in context.user_data:
        await handle_add_cours_main(user_id, text, update, context)
    elif "waiting_for_hour" in context.user_data:
        await handle_text_input(update, context)
    elif "modify_course" in context.user_data:
        module_name = context.user_data["modify_course"]["module"]
        old_name = context.user_data["modify_course"]["old_name"]
        result = modify_cours(module_name, old_name, text, user_id)
        if result == "success":
            await update.message.reply_text(f"Course '{old_name}' renamed to '{text}'.", reply_markup=back_cours_button())
        elif result == "duplicate_course":
            await update.message.reply_text(f"Course '{text}' already exists in module '{module_name}'.", reply_markup=back_cours_button())
        del context.user_data["modify_course"]
    elif "flashcard_state" in context.user_data:
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]

        if flashcard_state["step"] == "front":
            context.user_data["flashcard_state"]["front"] = text
            context.user_data["flashcard_state"]["step"] = "back"
            await update.message.reply_text("Veuillez maintenant saisir le <b>verso</b> de la carte mémoire. 🔄", reply_markup=back_cours_button(), parse_mode="HTML")
        elif flashcard_state["step"] == "back":
            front = context.user_data["flashcard_state"]["front"]
            back = text
            result = add_flashcard(module_name, course_name, front, back, user_id)
            if result == "success":
                await update.message.reply_text(f"✅ Flashcard added!\n<b>Front:</b> {front}\n<b>Back:</b> {back}", reply_markup=back_cours_button(), parse_mode="HTML")
            elif result == "duplicate_flashcard":
                await update.message.reply_text(f"Flashcard with front '{front}' already exists in this course.", reply_markup=back_cours_button())
            del context.user_data["flashcard_state"]
    elif "modify_flashcard" in context.user_data:
        state = context.user_data["modify_flashcard"]
        flashcard_id = state["id"]
        choice = state.get("choice")

        if choice == "modify_front":
            modify_flashcard(flashcard_id, new_front=text)
            await update.message.reply_text("Front updated!", reply_markup=back_cours_button())
            del context.user_data["modify_flashcard"]
        elif choice == "modify_back":
            modify_flashcard(flashcard_id, new_back=text)
            await update.message.reply_text("Back updated!", reply_markup=back_cours_button())
            del context.user_data["modify_flashcard"]
        elif choice == "modify_both":
            if "new_front" not in state:
                state["new_front"] = text
                await update.message.reply_text("Now enter the new BACK text:")
            else:
                modify_flashcard(flashcard_id, new_front=state["new_front"], new_back=text)
                await update.message.reply_text("Front and back updated!", reply_markup=back_cours_button())
                del context.user_data["modify_flashcard"]
    else:
        module_name = text
        modules = get_modules(user_id)
        if module_name in modules:
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=back_module_button())
            return
        result = add_module(module_name, user_id)
        if result == "success":
            await update.message.reply_text(f"Module '{module_name}' added!", reply_markup=back_module_button())
        elif result == "duplicate_module":
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=back_module_button())

def main() -> None:
    print("Starting bot...")
    application = Application.builder().token("8020889638:AAH41jObW4hcd1GJ-iDpYhiL8_jQwsxAt9g").build()
    print("Bot initialized. Adding handlers...")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.add_error_handler(error_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(check_notifications(application))
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
