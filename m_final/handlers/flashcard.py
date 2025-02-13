from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from .backBTN import back_cours_button,back_module_button
from data.storage import (
    add_flashcard, get_flashcards,modify_flashcard,delete_flashcard_by_id
)

# ajouter une nouvelle carte 
async def handler_add_flashcardupdate(update : Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    #   Handle "Add Flashcard" button clicks
    parts = clicked_button_data.split("_")
    print("add f",parts)
    if len(parts) == 3:  # Format: "add_flashcard_moduleName_courseName"
        _, module_name, course_name = parts
        context.user_data["flashcard_state"] = {
            "module": module_name,
            "course": course_name,
            "step": "front"  # First step: ask for the front of the flashcard
            }
        #Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        
        await query.edit_message_text("Veuillez saisir le <b>recto</b> de la carte mémoire.", reply_markup=reply_markup, parse_mode="HTML")


async def handler_add_flashcardupdate_main(update : Update, context: CallbackContext,text:str,user_id:int) -> None:
    
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]
        #Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if flashcard_state["step"] == "front":
            context.user_data["flashcard_state"]["front"] = text
            # Check if the flashcard with the given front text already exists
            if any(flashcard['front'] == text for flashcard in get_flashcards(module_name, course_name, user_id)):
                await update.message.reply_text(f"Une flashcard avec le recto <b>«{text}»</b> existe déjà dans <b>«{course_name}»</b>.", reply_markup=reply_markup,parse_mode="HTML")
                return
            context.user_data["flashcard_state"]["step"] = "back"
            await update.message.reply_text("Veuillez maintenant saisir le <b>verso</b> de la carte mémoire. 🔄", reply_markup=reply_markup, parse_mode="HTML")
        elif flashcard_state["step"] == "back":
            front = context.user_data["flashcard_state"]["front"]
            back = text
            
            result = add_flashcard(module_name, course_name, front, back, user_id)
            if result == "success":
                await update.message.reply_text(f"✅ Flashcard ajoutée !\n\n <b>Recto :</b> {front}\n <b>Verso :</b> {back} \n\n", reply_markup=reply_markup, parse_mode="HTML")
            elif result == "duplicate_flashcard":
                await update.message.reply_text(f"Une flashcard avec le recto <b>«{front}»</b> existe déjà dans <b>«{course_name}»</b>.", reply_markup=reply_markup,parse_mode="HTML")
            del context.user_data["flashcard_state"]

#--------------------------------------------------------------------------------------------------------
# afficher les flashcard d'un cours "c"

async def handler_list_flashcardupdate(update : Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    parts = clicked_button_data.split("_")
    if len(parts) == 3:  # Format: "list_flashcards_moduleName_courseName"
        _, module_name, course_name = parts
        flashcards = get_flashcards(module_name, course_name, user_id)
        #Create the keyboard with a back button
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['flashcardID']={
            "module": module_name,
            "course": course_name
        }
        if not flashcards:
            await query.edit_message_text(
                f"Aucune carte trouvée dans <b>« {course_name} »</b>.\n"
                "Allez dans « Ajouter une carte » pour en créer une.",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            # Create buttons with modify/delete options
            keyboard = [
                    [
                        InlineKeyboardButton(f" {f['front']}", callback_data=f"show_flashcard_{f['id']}"),
                        InlineKeyboardButton("✏️ Modifier", callback_data=f"modify_flashcard_{f['id']}_{course_name}_{module_name}"),
                        InlineKeyboardButton("🗑️ Supprimer", callback_data=f"delete_flashcard_{f['id']}")
                    ]
                for f in flashcards
                ]
            keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"module_{module_name}")])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Cartes du cours <b>«{course_name}»</b>:", reply_markup=reply_markup,parse_mode="HTML")

#---------------------------------------------------------------------------------------------------
# afficher front et back d'une carte 

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
            await query.edit_message_text(f"Carte du cours <b>«{course_name}»</b> du module <b>«{module_name}»</b> \n\n <b>Recto:</b> {flashcard['front']}\n <b>Verso:</b> {flashcard['back']}", reply_markup=reply_markup,parse_mode="HTML")
        else:
            await query.edit_message_text("Flashcard not found.", reply_markup=reply_markup)
    

#------------------------------------------------------------------------------------------------------------------
# modifier une carte 

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


async def handler_modify_flashcardupdate_main(update : Update, context: CallbackContext,text:str) -> None:
    state = context.user_data["modify_flashcard"]
    flashcard_id = state["id"]
    course_name=state["course"]
    module_name=state["module"]
    choice = state.get("choice")
    # back button
    keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"backListFlashcard_{module_name}_{course_name}")] # retour à la liste des cartes 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
        
    if choice == "modify_front":
        modify_flashcard(flashcard_id, new_front=text)
        await update.message.reply_text("✅ Recto mis à jour !", reply_markup=reply_markup)
        del context.user_data["modify_flashcard"]
        
    elif choice == "modify_back":
        modify_flashcard(flashcard_id, new_back=text)
        await update.message.reply_text("✅ Verso mis à jour !", reply_markup=reply_markup)
        del context.user_data["modify_flashcard"]
        
    elif choice == "modify_both":
        if "new_front" not in state:
            state["new_front"] = text
            await update.message.reply_text("Entrez maintenant le nouveau VERSO :")
        else:
            modify_flashcard(flashcard_id, new_front=state["new_front"], new_back=text)
            await update.message.reply_text("✅ Recto et verso mis à jour !", reply_markup=reply_markup)
            del context.user_data["modify_flashcard"]



async def handle_modify_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    choice = query.data  # "modify_front", "modify_back", or "modify_both"
    print("context user data : ",context.user_data)
    context.user_data["modify_flashcard"]["choice"] = choice
    
    if choice == "modify_front":
        await query.edit_message_text("Entrez le nouveau RECTO :")
    elif choice == "modify_back":
        await query.edit_message_text("Entrez le nouveau VERSO :")
    elif choice == "modify_both":
        await query.edit_message_text("Entrez d'abord le nouveau RECTO ")
    else:
        return





async def handle_delete_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "delete_flashcard_flashcardId"
        flashcard= context.user_data["flashcardID"]
        module_name = flashcard["module"]
        course_name = flashcard["course"]
        flashcard_id = int(parts[2])
        delete_flashcard_by_id(flashcard_id)
        #Create the keyboard with a back button --- retour à la liste des cartes 
        keyboard = [
            [InlineKeyboardButton("🔙 Retour", callback_data=f"backListFlashcard_{module_name}_{course_name}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("✅ Carte supprimée!", reply_markup=reply_markup)
        del context.user_data["flashcardID"]



