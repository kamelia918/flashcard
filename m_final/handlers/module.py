from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.storage import add_module, get_modules,modify_module,delete_module
from .backBTN import back_module_button

async def handle_add_module(update: Update, context: CallbackContext) -> None:
    module_name = update.message.text
    add_module(module_name)  # Add the module to storage
    
    modules = get_modules()
    
    # Create a list of buttons for each module
    keyboard = [
        [InlineKeyboardButton(module, callback_data=f"module_{module}")] for module in modules
    ]
    
    # Add an "Add Module" button
    keyboard.append([InlineKeyboardButton("Add Module", callback_data="add_module")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"Module '{module_name}' added!", reply_markup=reply_markup)



async def handle_list_modules(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id

    modules = get_modules(user_id)
    
        # Create a list of buttons for each module
    keyboard = []
    for module in modules:
        keyboard.append([
            InlineKeyboardButton(module, callback_data=f"module_{module}"),
            InlineKeyboardButton("✏️ Modifier", callback_data=f"modify_module_{module}"),
            InlineKeyboardButton("🗑️ Supprimer ", callback_data=f"delete_module_{module}")
        ])
        
        # Add an "Add Module" button
    keyboard.append([InlineKeyboardButton("➕ Ajouter un module ", callback_data="add_module")])
    # Add a "Back" button
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="back_to_start")])
                    
        
    reply_markup = InlineKeyboardMarkup(keyboard)
        
    if modules:
        await query.edit_message_text("Vos modules:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Aucun module ajouté pour l'instant. Cliquez sur <b>Ajouter un module</b> pour en créer un.", reply_markup=reply_markup, parse_mode="HTML")


async def handle_modify_module(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "modify_module_moduleName"
        _, _, module_name = parts
        context.user_data["modify_module"] = module_name
        await query.edit_message_text(f"Entrez le nouveau nom du module <b>{module_name}</b>:", reply_markup=back_module_button(),parse_mode="HTML")





async def modify_module_main(user_id: int, text: str, update: Update, context: CallbackContext) -> None:
    old_name = context.user_data.get("modify_module")  # Utiliser .get() pour éviter les erreurs
    if not old_name:
        await update.message.reply_text("Erreur : Pas de module à modifier.")
        return

    modules = get_modules(user_id)
    if text in modules:
        await update.message.reply_text(f"Module <b>«{text}»</b> existe déjà.", reply_markup=back_module_button(), parse_mode="HTML")
    else:
        try:
            modify_module(old_name, text, user_id)
            await update.message.reply_text(f"Module <b>«{old_name}»</b> renommé en <b>«{text}»</b>.", reply_markup=back_module_button(), parse_mode="HTML")
            del context.user_data["modify_module"]  # Nettoyer context.user_data
        except Exception as e:
            await update.message.reply_text(f"Erreur lors de la modification du module : {e}")

async def handle_delete_module(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) == 3:  # Format: "delete_module_moduleName"
        _, _, module_name = parts
        user_id = update.effective_user.id

        # Delete the module and its associated courses and flashcards
        delete_module(module_name, user_id)
        await query.edit_message_text(f"Le module <b>« {module_name} »</b> et tous ses cours/cartes mémoire ont été supprimés.", reply_markup=back_module_button(), parse_mode="HTML")
