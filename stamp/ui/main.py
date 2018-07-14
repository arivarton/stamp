from .ui import UI
from .status import main as status_ui


def main(stdscr):
    stamp_ui = UI(stdscr, ('in', 'status', 'delete'))
    stamp_ui.add_help()
    stamp_ui.add_options()
    stamp_ui.refresh()
    next_step = stamp_ui.interact()
    if next_step == 'status':
        status_ui(stdscr)
