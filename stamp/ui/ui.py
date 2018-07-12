import curses

from ..formatting import format_column


class UI:
    def __init__(self, stdscr):
        stdscr.keypad(True)
        stdscr_y, stdscr_x = stdscr.getmaxyx()
        self.bottom = stdscr_y - 1
        self.rightmost = stdscr_x - 1
        self.stdscr = stdscr
        self.pad = curses.newpad(self.bottom, self.rightmost)
        self.pad.refresh(0, 0, 0, 0, self.bottom, self.rightmost)
        self.pad_column_pos = 1
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)

    def add_left_string(self, y, string, *args, **kwargs):
        self.stdscr.addstr(y, 1, string, *args, **kwargs)

    def add_right_string(self, y, string, *args, **kwargs):
        self.stdscr.addstr(y, self.rightmost - len(string),
                           string, *args, **kwargs)

    def add_column(self, headline, rows, width, alignment='^'):
        self.pad.addstr(0, self.pad_column_pos,
                        format_column(headline, width, alignment=alignment),
                        curses.A_REVERSE|curses.A_BOLD)
        for line_number, row in enumerate(rows, 1):
            self.pad.addstr(line_number, self.pad_column_pos,
                            format_column(row, width, alignment=alignment),
                            curses.A_REVERSE)
        self.pad_column_pos += width + 1

    def refresh(self):
        self.pad.refresh(0, 0, 0, 0, self.bottom, self.rightmost)

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
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
