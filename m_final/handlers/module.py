from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from data.storage import add_module, get_modules

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
