import curses

from .ui import UI


def main(stdscr, test=None):
    stamp_ui = UI(stdscr)
    stamp_ui.add_menu()
    stamp_ui.add_column('Test1', ('sasa', 'tada'), 7)
    stamp_ui.add_column('Test2', ('xaxa', 'blbl'), 8)
    stamp_ui.refresh()
    stamp_ui.get_char()


curses.wrapper(main)
