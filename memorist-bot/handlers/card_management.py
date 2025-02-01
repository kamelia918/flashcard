import asyncio
import datetime
from os import times
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ContextTypes
from data.storage import modules


# Schedule the timer and send reminder
async def schedule_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, review_time: datetime.time) -> None:
    now = datetime.datetime.now()
    target_time = datetime.datetime.combine(now, review_time)
    if target_time < now:
        target_time += datetime.timedelta(days=1)
    delay = (target_time - now).total_seconds()

    await asyncio.sleep(delay)
    
    buttons = [
        [InlineKeyboardButton("Review", callback_data='revise')],
        [InlineKeyboardButton("Go back", callback_data='go_back')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Hey, it is time to review your flashcards!",
        reply_markup=reply_markup
    )


# Function to handle user input for adding modules, courses, and cards
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_step = context.user_data.get('current_step', '')

    if user_step == 'add_module':
        module_name = update.message.text
        if module_name in modules:
            await update.message.reply_text("This module already exists.")
        else:
            modules[module_name] = {}
            await update.message.reply_text(f"Module '{module_name}' has been created.")
        context.user_data['current_step'] = None

    elif user_step == 'add_cours':
        cours_name = update.message.text
        module_name = context.user_data.get('selected_module', '')
        if module_name and cours_name not in modules[module_name]:
            modules[module_name][cours_name] = []
            await update.message.reply_text(f"Cours '{cours_name}' has been added to module '{module_name}'.")
        else:
            await update.message.reply_text(f"Cours '{cours_name}' already exists in module '{module_name}'.")
        context.user_data['current_step'] = None

    elif user_step == 'front':
        context.user_data['card_front'] = update.message.text
        context.user_data['current_step'] = 'back'
        buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Please enter the back of the card.", reply_markup=reply_markup)

    elif user_step == 'back':
        card_back = update.message.text
        card_front = context.user_data.get('card_front', '')
        buttons = [[InlineKeyboardButton(mod, callback_data=f"store_card_module_{mod}")] for mod in modules]
        buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Please choose the module to store the card in:", reply_markup=reply_markup)
        context.user_data['card_back'] = card_back

    elif user_step == 'timer':
        time_input = update.message.text
        try:
            review_time = datetime.datetime.strptime(time_input, "%H:%M").time()
            times[update.message.chat_id] = review_time
            await update.message.reply_text(f"Timer set for {review_time.strftime('%H:%M')}!")
            await schedule_timer(update, context, review_time)
        except ValueError:
            await update.message.reply_text("Invalid time format. Please enter a time in HH:MM format.")
        context.user_data['current_step'] = None

    else:
        await update.message.reply_text("I don't understand your input.")

# Function to add a card
async def add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['current_step'] = 'front'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please enter the front of the card (text, image, or voice).", reply_markup=reply_markup)

# Function to store a card in a chosen module and cours
async def store_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    module_name = query.data.replace('store_card_module_', '')
    context.user_data['selected_module'] = module_name
    buttons = [[InlineKeyboardButton(cours, callback_data=f"store_card_cours_{cours}")] for cours in modules[module_name]]
    buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(f"Please choose the cours to store the card in:", reply_markup=reply_markup)

# Function to store a card in a specific cours
async def store_card_in_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cours_name = query.data.replace('store_card_cours_', '')
    module_name = context.user_data['selected_module']
    card_front = context.user_data.get('card_front', '')
    card_back = context.user_data.get('card_back', '')
    modules[module_name][cours_name].append({'front': card_front, 'back': card_back})
    await query.message.reply_text(f"Card has been stored in '{cours_name}' in module '{module_name}'.")

# Register all card management handlers
card_management_handlers = [
    CallbackQueryHandler(add_card, pattern='add_card'),
    CallbackQueryHandler(store_card, pattern='store_card_module_'),
    CallbackQueryHandler(store_card_in_cours, pattern='store_card_cours_'),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
]