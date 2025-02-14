from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
from data.storage import get_due_flashcards, get_flashcards

async def handler_revise_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 3:
        _, module_name, course_name = parts
        due_flashcards = get_flashcards(module_name, course_name, user_id)

        if not due_flashcards:
            keyboard = [
                [InlineKeyboardButton("Retour", callback_data=f"course_{module_name}_{course_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Aucune flashcard à réviser.", reply_markup=reply_markup)
        else:
            random.shuffle(due_flashcards)
            context.user_data["revision_state"] = {
                "module": module_name,
                "course": course_name,
                "flashcards": due_flashcards,
                "current_index": 0,
                "score": 0,
                "forgotten_flashcards": []
            }
            await show_next_flashcard(update, context)

async def show_next_flashcard(update: Update, context: CallbackContext) -> None:
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return

    flashcards = revision_state["flashcards"]
    current_index = revision_state["current_index"]

    if current_index >= len(flashcards):
        score = revision_state["score"]
        total_flashcards = len(flashcards)
        keyboard = [
            [InlineKeyboardButton("Redémarrer la révision", callback_data="restart_revision")],
            [InlineKeyboardButton("Retour", callback_data="back_to_modules")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        forgotten_flashcards = revision_state.get("forgotten_flashcards", [])
        if forgotten_flashcards:
            forgotten_text = "\n".join([f"❌ <b>{fc['front']}</b> - {fc['back']}" for fc in forgotten_flashcards])
            forgotten_message = f"\n\n⚠️ Flashcards oubliées :\n{forgotten_text}"
        else:
            forgotten_message = "\n\n👏 Aucune flashcard oubliée ! Bien joué !"

        score_on_20 = (score / total_flashcards) * 20

        if score_on_20 < 10:
            message = (
                f"😢 Session de révision terminée...\n\n"
                f"❌ Vous avez {score}/{total_flashcards} bonnes réponses.\n\n"
                f"📉 Note : {score_on_20:.2f}/20\n\n"
                "💡 Ne vous découragez pas ! Revoyez les cartes et réessayez. 💪"
                f"{forgotten_message}"
            )
        elif 10 <= score_on_20 < 15:
            message = (
                f"🙂 Session de révision terminée !\n\n"
                f"✅ Vous avez {score}/{total_flashcards} bonnes réponses.\n\n"
                f"📊 Note : {score_on_20:.2f}/20\n\n"
                "👏 Pas mal, mais vous pouvez encore vous améliorer ! Continuez ! 🚀"
                f"{forgotten_message}"
            )
        else:
            message = (
                f"🎉 Session de révision terminée !\n\n"
                f"✅ Vous avez {score}/{total_flashcards} bonnes réponses.\n\n"
                f"🌟 Note : {score_on_20:.2f}/20\n\n"
                "🎯 Excellent travail ! Vous êtes un(e) champion(ne) ! 🏆"
                f"{forgotten_message}"
            )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    flashcard = flashcards[current_index]
    keyboard = [
        [InlineKeyboardButton("Afficher le verso", callback_data=f"show_back_{current_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if flashcard['front'].startswith('photos/'):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(flashcard['front'], 'rb'), caption=f"Flashcard {current_index + 1}/{len(flashcards)}", reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Flashcard {current_index + 1}/{len(flashcards)}\nRecto: {flashcard['front']}",
            reply_markup=reply_markup
        )

async def handle_show_back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return

    parts = query.data.split("_")
    if len(parts) == 3:
        current_index = int(parts[2])
        flashcard = revision_state["flashcards"][current_index]
        keyboard = [
            [InlineKeyboardButton("Oui", callback_data=f"remembered_{current_index}")],
            [InlineKeyboardButton("Non", callback_data=f"forgot_{current_index}")]
        ]

        if current_index == len(revision_state["flashcards"]) - 1:
            keyboard.append([InlineKeyboardButton("Redémarrer la révision", callback_data="restart_revision")])
        else:
            keyboard.append([InlineKeyboardButton("Carte suivante", callback_data=f"next_card_{current_index}")])

        keyboard.append([InlineKeyboardButton("Retour", callback_data="back_to_modules")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        if flashcard['front'].startswith('photos/'):
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(flashcard['front'], 'rb'), caption=f"Verso: {flashcard['back']}\nVous vous en souvenez?", reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Recto: {flashcard['front']}\nVerso: {flashcard['back']}\nVous vous en souvenez?",
                reply_markup=reply_markup
            )

async def handle_revision_feedback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 2:
        feedback, index = parts
        revision_state = context.user_data.get("revision_state")
        if not revision_state:
            return

        if feedback == "remembered":
            revision_state["score"] += 1
        elif feedback == "forgot":
            current_index = revision_state["current_index"]
            flashcards = revision_state["flashcards"]
            if current_index < len(flashcards):
                current_flashcard = flashcards[current_index]
                revision_state.setdefault("forgotten_flashcards", []).append({
                    "front": current_flashcard["front"],
                    "back": current_flashcard["back"]
                })

        revision_state["current_index"] += 1
        await show_next_flashcard(update, context)

async def handle_next_card(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return

    revision_state["current_index"] += 1
    await show_next_flashcard(update, context)

async def handle_restart_revision(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
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
            keyboard = [
                [InlineKeyboardButton("Retour", callback_data=f"course_{module_name}_{course_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Impossible de redémarrer la révision. Veuillez démarrer une nouvelle session.", reply_markup=reply_markup)
        return

    revision_state["current_index"] = 0
    revision_state["score"] = 0
    random.shuffle(revision_state["flashcards"])
    await show_next_flashcard(update, context)