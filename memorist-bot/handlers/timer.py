# This file contains the timer-related handlers.

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import datetime
import asyncio

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_step'] = 'timer'
    await update.message.reply_text("Please enter the time (e.g., 10:30) when you'd like to review your flashcards.")

async def handle_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('current_step') == 'timer':
        time_input = update.message.text
        try:
            review_time = datetime.datetime.strptime(time_input, "%H:%M").time()
            await update.message.reply_text(f"Timer set for {review_time.strftime('%H:%M')}!")
        except ValueError:
            await update.message.reply_text("Invalid time format. Please enter a time in HH:MM format.")
        context.user_data['current_step'] = None

timer_handler = CommandHandler("timer", set_timer)