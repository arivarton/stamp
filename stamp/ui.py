import curses


class UI:
    def __init__(self, stdscr):
        stdscr.keypad(True)
        stdscr_y, stdscr_x = stdscr.getmaxyx()
        self.bottom = stdscr_y - 1
        self.rightmost = stdscr_x - 1
        self.stdscr = stdscr
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)

    def add_left_string(self, y, string, *args, **kwargs):
        self.stdscr.addstr(y, 1, string, *args, **kwargs)

    def add_right_string(self, y, string, *args, **kwargs):
        self.stdscr.addstr(y, self.rightmost - len(string),
                           string, *args, **kwargs)

    def add_menu(self):
        self.add_left_string(self.bottom, 'Some option',
                             curses.A_REVERSE)
        self.add_right_string(self.bottom, 'q to quit',
                              curses.A_REVERSE)
        self.stdscr.refresh()

    def get_char(self):
        while True:
            if self.stdscr.getch(0, 0) == ord('q'):
                break

    def terminate(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()


stamp_ui = curses.wrapper(UI)
stamp_ui.add_menu()
stamp_ui.get_char()
