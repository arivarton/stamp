from .ui import UI


def main(stdscr):
    stamp_ui = UI(stdscr)
    stamp_ui.add_help()
    stamp_ui.add_options(('in', 'status', 'delete'))
    stamp_ui.refresh()
    stamp_ui.get_char()
