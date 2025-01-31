from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import random
import datetime
import asyncio

# Memory storage for simplicity. In real case, use a database
modules = {}
timers = {}

# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [InlineKeyboardButton("Add a card", callback_data='add_card')],
        [InlineKeyboardButton("Revise", callback_data='revise')],
        [InlineKeyboardButton("Set timer for revision", callback_data='set_timer')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Welcome to Memorist, a telegram bot sepcially developed to help you with recalling information and retaining it for long periods of time through active recall. If you want to maximize it, we suggest that you use the spaced repetition technique to enhance your recalling. Before adding cards, use the command /module pour ajouter un module, then use the command /cours pour ajouter un cours. Only after creating these 2 you can proceeed by adding cards by clicking on the Add a card button. If you already have your cards and you're here simply for reviewing them, click the button Revise, to start revision. Here is a link for the explainer video if anything was unclear to you :    make sure to leave us your feedback, good luck and Aspire to achieve :D",
        reply_markup=reply_markup
    )

# "Go back" button function
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query:  # If the update is a callback query (button click)
        await update.callback_query.answer()  # Acknowledge the callback query
        await start(update.callback_query, context)  # Call start as a callback query
    elif update.message:  # If the update is a message (typed command)
        await start(update, context)  # Call start as a normal message



# Command to add a new module
async def add_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_step'] = 'add_module'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Please enter the name of the new module.", reply_markup=reply_markup)

# Command to add a new cours (deck) inside a module
async def add_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if modules:
        buttons = [[InlineKeyboardButton(mod, callback_data=f"add_cours_module_{mod}")] for mod in modules]
        buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Please choose the module to add the cours:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No modules available. Please create a module first using /module command.")

# Handling module selection for adding cours
async def choose_module_for_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    module_name = query.data.replace('add_cours_module_', '')
    context.user_data['selected_module'] = module_name
    context.user_data['current_step'] = 'add_cours'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(f"Enter the name of the new cours to add to module '{module_name}'.", reply_markup=reply_markup)

# Handling user input for adding modules and cours
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
            timers[update.message.chat_id] = review_time
            await update.message.reply_text(f"Timer set for {review_time.strftime('%H:%M')}!")
            await schedule_timer(update, context, review_time)
        except ValueError:
            await update.message.reply_text("Invalid time format. Please enter a time in HH:MM format.")
        context.user_data['current_step'] = None

    else:
        await update.message.reply_text("I don't understand your input.")

# Define the add card flow
async def add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['current_step'] = 'front'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please enter the front of the card (text, image, or voice).", reply_markup=reply_markup)

# Storing the card in the chosen module and cours
async def store_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    module_name = query.data.replace('store_card_module_', '')
    context.user_data['selected_module'] = module_name
    buttons = [[InlineKeyboardButton(cours, callback_data=f"store_card_cours_{cours}")] for cours in modules[module_name]]
    buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(f"Please choose the cours to store the card in:", reply_markup=reply_markup)

async def store_card_in_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cours_name = query.data.replace('store_card_cours_', '')
    module_name = context.user_data['selected_module']
    card_front = context.user_data.get('card_front', '')
    card_back = context.user_data.get('card_back', '')
    modules[module_name][cours_name].append({'front': card_front, 'back': card_back})
    await query.message.reply_text(f"Card has been stored in '{cours_name}' in module '{module_name}'.")

# Set timer for revision
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data['current_step'] = 'timer'
    buttons = [[InlineKeyboardButton("Go back", callback_data='go_back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please enter the time (e.g., 10:30) when you'd like to review your flashcards.", reply_markup=reply_markup)

async def handle_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('current_step') == 'timer':
        time_input = update.message.text
        try:
            review_time = datetime.datetime.strptime(time_input, "%H:%M").time()
            timers[update.message.chat_id] = review_time
            await update.message.reply_text(f"Timer set for {review_time.strftime('%H:%M')}!")
            await schedule_timer(update, context, review_time)
        except ValueError:
            await update.message.reply_text("Invalid time format. Please enter a time in HH:MM format.")
        context.user_data['current_step'] = None

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

# List available modules for revising
async def list_modules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if modules:
        buttons = [[InlineKeyboardButton(mod, callback_data=f"revise_module_{mod}")] for mod in modules]
        buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.message.reply_text("Please choose a module to revise:", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("No modules available. Please create a module first using /module command.")

# List available cours for revising within a selected module
async def choose_module_for_revise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    module_name = query.data.replace('revise_module_', '')
    context.user_data['selected_module'] = module_name
    buttons = [[InlineKeyboardButton(cours, callback_data=f"revise_cours_{cours}")] for cours in modules[module_name]]
    buttons.append([InlineKeyboardButton("Go back", callback_data='go_back')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(f"Please choose a cours to revise from module '{module_name}':", reply_markup=reply_markup)

# Start revision of the selected cours
async def revise_cours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    cours_name = query.data.replace('revise_cours_', '')
    module_name = context.user_data['selected_module']
    context.user_data['cards'] = modules[module_name][cours_name]
    context.user_data['current_card_index'] = 0
    context.user_data['correct'] = 0
    context.user_data['incorrect'] = 0
    await send_next_card(update, context)

async def send_next_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    index = context.user_data['current_card_index']
    cards = context.user_data['cards']
    if index < len(cards):
        card = cards[index]
        buttons = [
            [InlineKeyboardButton("Show Back", callback_data='show_back')],
            [InlineKeyboardButton("Go back", callback_data='go_back')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.message.reply_text(f"Card front: {card['front']}", reply_markup=reply_markup)
    else:
        correct = context.user_data.get('correct', 0)
        incorrect = context.user_data.get('incorrect', 0)
        total = correct + incorrect
        grade = (correct / total) * 20 if total > 0 else 0
        await update.callback_query.message.reply_text(f"Revision complete! You scored {grade}/20.")
        await go_back(update, context)

async def show_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    index = context.user_data['current_card_index']
    cards = context.user_data['cards']
    card = cards[index]
    buttons = [
        [InlineKeyboardButton("Correct", callback_data='correct')],
        [InlineKeyboardButton("Incorrect", callback_data='incorrect')],
        [InlineKeyboardButton("Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.callback_query.message.reply_text(f"Card back: {card['back']}", reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data == 'correct':
        context.user_data['correct'] += 1
    elif query.data == 'incorrect':
        context.user_data['incorrect'] += 1
    elif query.data == 'exit':
        await go_back(update, context)
        return

    context.user_data['current_card_index'] += 1
    await send_next_card(update, context)

# Main function to run the bot
def main() -> None:
    application = Application.builder().token("7408230027:AAGbM2T_8fNSs8anCyr8bb2xRm7SER6yjhE").build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("module", add_module))
    application.add_handler(CommandHandler("cours", add_cours))
    application.add_handler(CommandHandler("timer", set_timer))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(add_card, pattern='add_card'))
    application.add_handler(CallbackQueryHandler(choose_module_for_cours, pattern='add_cours_module_'))
    application.add_handler(CallbackQueryHandler(store_card, pattern='store_card_module_'))
    application.add_handler(CallbackQueryHandler(store_card_in_cours, pattern='store_card_cours_'))
    application.add_handler(CallbackQueryHandler(set_timer, pattern='set_timer'))
    application.add_handler(CallbackQueryHandler(go_back, pattern='go_back'))
    application.add_handler(CallbackQueryHandler(choose_module_for_revise, pattern='revise_module_'))
    application.add_handler(CallbackQueryHandler(revise_cours, pattern='revise_cours_'))
    application.add_handler(CallbackQueryHandler(show_back, pattern='show_back'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='correct|incorrect|exit'))
    application.add_handler(CallbackQueryHandler(list_modules, pattern='revise'))  # Added revise handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timer))

    application.run_polling()


if __name__ == "__main__":
    main()
