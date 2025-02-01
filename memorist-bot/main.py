# #This file will initialize the bot and register all handlers.

# from telegram.ext import Application
# from handlers import start, add_module, add_cours, revise, timer, card_management
# from data.storage import modules, timers

# def main() -> None:
#     application = Application.builder().token("7408230027:AAGbM2T_8fNSs8anCyr8bb2xRm7SER6yjhE").build()

#     # Register command handlers
#     application.add_handler(start.start_handler)
#     application.add_handler(add_module.add_module_handler)
#     application.add_handler(add_cours.add_cours_handler)
#     application.add_handler(revise.revise_handler)
#     application.add_handler(timer.timer_handler)

#     # Register message and callback handlers
#     application.add_handler(card_management.card_management_handlers)

#     # Start the bot
#     application.run_polling()

# if __name__ == "__main__":
#     main()
from telegram.ext import Application
from handlers import start, add_module, add_cours, revise, timer, card_management

def main() -> None:
    print("Starting bot...")  # Debugging log

    application = Application.builder().token("7758636605:AAE3iDboYqy-5FSH2iXwUgF4_YlvkVKpBGo").build()
    
    print("Bot initialized. Adding handlers...")  # Debugging log

    # Register command handlers
    application.add_handler(start.start_handler)
    application.add_handler(add_module.add_module_handler)
    application.add_handler(add_cours.add_cours_handler)
    application.add_handler(revise.revise_handler)
    application.add_handler(timer.timer_handler)

    # Register multiple handlers from card_management
    for handler in card_management.card_management_handlers:
        application.add_handler(handler)

    print("All handlers added. Running polling...")  # Debugging log

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
