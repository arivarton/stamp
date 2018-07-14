from .ui import UI


def main(stdscr):
    stamp_ui = UI(stdscr)
    stamp_ui.add_help()
    stamp_ui.add_column('Test1', ('sasa', 'tada'), 7)
    stamp_ui.add_column('Test2', ('xaxa', 'blbl'), 8)
    stamp_ui.refresh()
    stamp_ui.interact()
