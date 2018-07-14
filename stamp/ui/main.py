from .ui import UI


def main(stdscr):
    stamp_ui = UI(stdscr, ('in', 'status', 'delete'))
    stamp_ui.add_help()
    stamp_ui.add_options()
    stamp_ui.refresh()
    stamp_ui.interact()
