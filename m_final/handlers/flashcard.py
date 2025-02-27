from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import re
from .backBTN import back_cours_button, back_module_button
from data.storage import (
    add_flashcard, get_flashcards, modify_flashcard, delete_flashcard_by_id
)

async def handler_add_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 3:
        _, module_name, course_name = parts
        context.user_data["flashcard_state"] = {
            "module": module_name,
            "course": course_name,
            "step": "front"
        }
        keyboard = [
            [InlineKeyboardButton("📝 Texte", callback_data="add_text")],
            [InlineKeyboardButton("📸 Photo", callback_data="add_photo")],
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Veuillez saisir le <b>recto</b> de la carte mémoire.", reply_markup=reply_markup, parse_mode="HTML")

async def handler_add_flashcardupdate_main(update: Update, context: CallbackContext, text: str, user_id: int) -> None:
    flashcard_state = context.user_data["flashcard_state"]
    module_name = flashcard_state["module"]
    course_name = flashcard_state["course"]

    keyboard = [
        [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if flashcard_state["step"] == "front":
        context.user_data["flashcard_state"]["front"] = text
        context.user_data["flashcard_state"]["step"] = "back"
        await update.message.reply_text("Veuillez maintenant saisir le <b>verso</b> de la carte mémoire. 🔄", reply_markup=reply_markup, parse_mode="HTML")
    elif flashcard_state["step"] == "back":
        front = context.user_data["flashcard_state"]["front"]
        back = text
        result = add_flashcard(module_name, course_name, front, back, user_id)
        match = re.match(r"(.+?) \(([^)]+)\)", front)  # Ex : "Titre (chemin/image.jpg)"
        if match:
            front_display = match.group(1)  # Récupère uniquement le titre
        if result == "success":
            try:
                if front.startswith('photos/'):
                    await update.message.reply_text(
                        f"✅ Flashcard ajoutée !\n\n <b>Recto :</b> photo\n <b>Verso :</b> {back} \n\n",
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                else:
                    await update.message.reply_text(
                        f"✅ Flashcard ajoutée !\n\n <b>Recto :</b> {front_display}\n <b>Verso :</b> {back} \n\n",
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
            except Exception as e:
                await update.message.reply_text(f"✅ Flashcard ajoutée !\n\n <b>Recto :</b> {front}\n <b>Verso :</b> {back} \n\n",
                        reply_markup=reply_markup,
                        parse_mode="HTML")

        elif result == "duplicate_flashcard":
            await update.message.reply_text(f"Flashcard avec le recto '{front}' existe déjà dans ce cours.", reply_markup=back_cours_button())
        del context.user_data["flashcard_state"]

async def handler_list_flashcardupdate(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 3:
        _, module_name, course_name = parts
        flashcards = get_flashcards(module_name, course_name, user_id)
        keyboard = []
       
        reply_markup = InlineKeyboardMarkup(keyboard)
        if not flashcards:
            await query.edit_message_text("Aucune flashcard trouvée.", reply_markup=reply_markup)
        else:
            for f in flashcards:
                front_display = f["front"]
                
                # Extraire seulement le titre si un chemin d’image est inclus
                match = re.match(r"(.+?) \(([^)]+)\)", f["front"])  # Ex : "Titre (chemin/image.jpg)"
                if match:
                    front_display = match.group(1)  # Récupère uniquement le titre
                
                keyboard.append([
                    InlineKeyboardButton(f"Recto: {front_display}", callback_data=f"show_flashcard_{f['id']}"),
                    InlineKeyboardButton("✏️ Modifier", callback_data=f"modify_flashcard_{f['id']}_{course_name}_{module_name}"),
                    InlineKeyboardButton("🗑️ Supprimer", callback_data=f"delete_flashcard_{f['id']}")
                ])


            keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Flashcards:", reply_markup=reply_markup)

async def handler_modify_flashcardupdate_main(update: Update, context: CallbackContext, text: str) -> None:
    state = context.user_data["modify_flashcard"]
    flashcard_id = state["id"]
    course_name = state["course"]
    module_name = state["module"]
    choice = state.get("choice")

    keyboard = [
        [InlineKeyboardButton("🔙 Retour", callback_data=f"backListFlashcard_{module_name}_{course_name}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if choice == "modify_front":
        # Récupérer la flashcard actuelle pour vérifier si elle a déjà une image
        module_name = context.user_data.get('module_name') # Récupérer module_name si nécessaire (peut être déjà dans state)
        course_name = context.user_data.get('course_name') # Récupérer course_name si nécessaire (peut être déjà dans state)
        user_id = update.effective_user.id
        all_flashcards = get_flashcards(module_name, course_name, user_id) # Récupérer toutes les flashcards pour retrouver celle à modifier
        current_flashcard = next((f for f in all_flashcards if str(f['id']) == flashcard_id), None)

        if current_flashcard:
            front_content = current_flashcard['front']
            image_path_match = re.search(r'\(([^)]+)\)', front_content)
            existing_image_path = image_path_match.group(1) if image_path_match else None

            if existing_image_path:
                # Si un chemin d'image existe, reconstruire le nouveau recto avec le nouveau titre et l'ancien chemin
                new_front_content = f"{text} ({existing_image_path})"
                modify_flashcard(flashcard_id, new_front=new_front_content)
                await update.message.reply_text("Titre de l'image mis à jour!", reply_markup=reply_markup)
            else:
                # Si pas de chemin d'image, traiter comme une modification de texte simple (comme avant)
                modify_flashcard(flashcard_id, new_front=text)
                await update.message.reply_text("Texte du recto mis à jour!", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Flashcard introuvable.", reply_markup=reply_markup) # Gestion d'erreur si flashcard non trouvée

        del context.user_data["modify_flashcard"]

    elif choice == "modify_back":
        modify_flashcard(flashcard_id, new_back=text)
        await update.message.reply_text("Verso mis à jour!", reply_markup=reply_markup)
        del context.user_data["modify_flashcard"]
    elif choice == "modify_both":
        if "new_front" not in state:
            state["new_front"] = text
            await update.message.reply_text("Veuillez maintenant saisir le nouveau texte pour le verso:")
        else:
            new_front = state["new_front"] if not state["new_front"].startswith('photos/') else text
            modify_flashcard(flashcard_id, new_front=new_front, new_back=text)
            await update.message.reply_text("Recto et verso mis à jour!", reply_markup=reply_markup)
            del context.user_data["modify_flashcard"]



async def handle_modify_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["modify_flashcard"]["choice"] = choice
    if choice == "modify_front":
        await query.edit_message_text("Envoyez la nouvelle photo ou entrez le nouveau texte pour le recto:")
    elif choice == "modify_back":
        await query.edit_message_text("Entrez le nouveau texte pour le verso:")
    elif choice == "modify_both":
        await query.edit_message_text("Envoyez d'abord la nouvelle photo ou entrez le nouveau texte pour le recto:")


async def handle_delete_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    if len(parts) == 3:
        flashcard_id = int(parts[2])
        delete_flashcard_by_id(flashcard_id)
        await query.edit_message_text("Flashcard supprimée!", reply_markup=back_module_button())








async def handle_modify_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    if len(parts) == 5:  # Format: "modify_flashcard_flashcardId"
        _,_,flashcard_id,course_name,module_name = parts
        
        context.user_data["modify_flashcard"] = {
            "id": flashcard_id,
            "step": "choose_field",
            "course":course_name,
            "module":module_name
        }
        
        # Ask user what to modify
        keyboard = [
            [InlineKeyboardButton("Recto", callback_data="modify_front")],
            [InlineKeyboardButton("Verso", callback_data="modify_back")],
            [InlineKeyboardButton("Recto & Verso", callback_data="modify_both")],
            [InlineKeyboardButton("🔙 Retour", callback_data=f"backListFlashcard_{module_name}_{course_name}")] # retour à la liste des cartes 
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("❓ Que souhaitez-vous modifier ?", reply_markup=reply_markup)







async def handle_show_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    # Gérer les clics de bouton flashcard (révéler le verso)
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    parts = clicked_button_data.split("_")
    if len(parts) == 3:  # Format: "show_flashcard_flashcardId"
        _, _, flashcard_id = parts
        # Récupérer les informations du module et du cours depuis context.user_data
        module_name = context.user_data.get('module_name')
        course_name = context.user_data.get('course_name')
        #Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"backListFlashcard_{module_name}_{course_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if not module_name or not course_name:
            await query.edit_message_text("Erreur : Module ou cours non spécifié.")
            return
        user_id = update.effective_user.id
        # Récupérer toutes les flashcards du storage
        all_flashcards = get_flashcards(module_name, course_name, user_id)
        # Rechercher la flashcard avec l'ID correspondant
        flashcard = next((f for f in all_flashcards if str(f['id']) == flashcard_id), None)
        if flashcard:
            front_display = flashcard['front']

            # Extraire uniquement le titre si un chemin d’image est inclus
            match = re.match(r"(.+?) \(([^)]+)\)", flashcard['front'])
            if match:
                front_display = match.group(1)  # Récupère uniquement le titre


            await query.edit_message_text(
                f"Carte du cours <b>«{course_name}»</b> du module <b>«{module_name}»</b> \n\n"
                f"<b>Recto:</b> {front_display}\n"
                f"<b>Verso:</b> {flashcard['back']}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
