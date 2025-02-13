from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
from data.storage import get_due_flashcards , get_flashcards

# commencer la revision de flashcards d'un cours "c"
async def handler_revise_flashcardupdate(update : Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    parts = clicked_button_data.split("_")
    if len(parts) == 3:  # Format: "revise_moduleName_courseName"
        _, module_name, course_name = parts
        due_flashcards = get_flashcards(module_name, course_name, user_id)  # Fetch due flashcards
        
        if not due_flashcards:
            # retrour à la liste des cours 
            keyboard=[[InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]]
                
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(f"Aucune carte à réviser dans le cours <b>«{course_name}»</b>.", reply_markup=reply_markup,parse_mode="HTML")
        else:
            # Shuffle flashcards for random order
            random.shuffle(due_flashcards)
            
            # Start the revision session
            context.user_data["revision_state"] = {
                "module": module_name,
                "course": course_name,
                "flashcards": due_flashcards,
                "current_index": 0,
                "score": 0,  # Initialize score
                "forgotten_flashcards": [] # pour sauvegarder les flashcard oublié
            }
            await show_next_flashcard(update, context)

# montrer la carte suivante a reviser
async def show_next_flashcard(update: Update, context: CallbackContext) -> None:
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    flashcards = revision_state["flashcards"]
    current_index = revision_state["current_index"]
    module_name = revision_state["module"]
    forgotten_flashcards = revision_state.get("forgotten_flashcards", [])

    if current_index >= len(flashcards):
        # End of revision session
        score = revision_state["score"]
        total_flashcards = len(flashcards)
        
        # Create keyboard with "Restart Revision" and "Back" buttons
        keyboard = [
            [InlineKeyboardButton("🔄 Recommencer la revision ", callback_data="restart_revision")],
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Formatage des flashcards oubliées
        if forgotten_flashcards:
            forgotten_text = "\n".join([f"❌ <b>{fc['front']}</b> - {fc['back']}" for fc in forgotten_flashcards])
            forgotten_message = f"\n\n⚠️ Flashcards oubliées :\n{forgotten_text}"
        else:
            forgotten_message = "\n\n👏 Aucune flashcard oubliée ! Bien joué !"

        # Calcul de la note sur 20
        score_on_20 = (score / total_flashcards) * 20

        # Création du message 
        # Création du message avec des conditions basées sur la note
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

        # Afficher ou envoyer le message
        await update.callback_query.edit_message_text(message,reply_markup=reply_markup,parse_mode="HTML")

        # del context.user_data["revision_state"]
        return
    
    flashcard = flashcards[current_index]
    keyboard = [
        [InlineKeyboardButton("Afficher le Verso", callback_data=f"show_back_{current_index}")]
    ]
    #  --- back to courses
    keyboard.append([InlineKeyboardButton("🔙 Arreter la revision", callback_data=f"module_{module_name}")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"Carte : <b>{current_index + 1}/{len(flashcards)}</b> \n\nRECTO: <b>{flashcard['front']}</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


# montrer le verso (la reponse)
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
        module_name=revision_state["module"]
        # Create buttons for feedback
        keyboard = [
            [InlineKeyboardButton("✅ Je m'en souviens", callback_data=f"remembered_{current_index}")],
            [InlineKeyboardButton("❌ J'ai oublié", callback_data=f"forgot_{current_index}")]
        ]
        
        # If it's the last flashcard, add "Restart Revision" button
        if current_index == len(revision_state["flashcards"]) - 1:
            [InlineKeyboardButton("🔄 Recommencer la revision ", callback_data="restart_revision")],
                
        # Add a "Back" button --- back to courses
        keyboard.append([InlineKeyboardButton("🔙 Arreter la revision", callback_data=f"module_{module_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"<b>RECTO:</b> {flashcard['front']}\n\n<b>Verso:</b> {flashcard['back']}\n\n🧠 Vous vous en souvenez ?",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# feedback to see if he did or not remember the flashcard
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
        # else: on ne fait rien
        
        # Move to the next flashcard
        revision_state["current_index"] += 1
        await show_next_flashcard(update, context)
# Feedback pour savoir si l'utilisateur se souvient ou non de la flashcard
async def handle_revision_feedback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    
    if len(parts) == 2:  # Format: "remembered_index" ou "forgot_index"
        feedback, index = parts
        index = int(index)  # Convertir l'index en entier
        revision_state = context.user_data.get("revision_state")
        
        if not revision_state:
            return
        
        # Mise à jour de l'état selon la réponse de l'utilisateur
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
                })# Ajouter à la liste des oubliées
            
            
        # Passer à la flashcard suivante
        revision_state["current_index"] += 1
        
        # Afficher la prochaine flashcard
        await show_next_flashcard(update, context)


# prochaine carte a reviser 
async def handle_next_card(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    revision_state = context.user_data.get("revision_state")
    if not revision_state:
        return
    
    # Move to the next flashcard
    revision_state["current_index"] += 1
    await show_next_flashcard(update, context)


# recommancer la revision 
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
            keyboard=[]
            keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")])
                
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text("Could not restart revision. Please start a new session.", reply_markup=reply_markup)
        return
    
    # Restart the revision session with existing data
    revision_state["current_index"] = 0
    revision_state["score"] = 0
    random.shuffle(revision_state["flashcards"])  # Shuffle again for randomness
    await show_next_flashcard(update, context)

