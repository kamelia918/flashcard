from .start import start_handler
from .add_module import add_module_handler
from .add_cours import add_cours_handler
from .revise import revise_handler
from .timer import timer_handler
from .card_management import card_management_handlers
# from .utils import setup_utils

def register_handlers(dp):
    """Register all handlers to the dispatcher."""
    start_handler(dp)
    add_module_handler(dp)
    add_cours_handler(dp)
    revise_handler(dp)
    timer_handler(dp)
    card_management_handlers(dp)
    # setup_utils(dp)
