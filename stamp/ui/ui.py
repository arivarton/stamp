import curses

from ..formatting import format_column


class UI(object):
    def __init__(self, stdscr, options=None):
        stdscr.keypad(True)
        stdscr_y, stdscr_x = stdscr.getmaxyx()
        self.bottom = stdscr_y - 1
        self.rightmost = stdscr_x - 1
        self.stdscr = stdscr
        self.pad = curses.newpad(self.bottom, self.rightmost)
        self.pad.move(1, 1)
        self.cursor_y, self.cursor_x = curses.getsyx()
        self.pad.refresh(0, 0, 0, 0, self.bottom, self.rightmost)
        self.pad_column_pos = 1
        self.options = options
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
                        curses.A_REVERSE|curses.A_BOLD) # NOQA
        for line_number, row in enumerate(rows, 1):
            self.pad.addstr(line_number, self.pad_column_pos,
                            format_column(row, width, alignment=alignment),
                            curses.A_REVERSE)
        self.pad_column_pos += width + 1

    def add_options(self, alignment='^'):
        for line_number, option in enumerate(self.options):
            if self.cursor_y == line_number:
                self.pad.addstr(line_number, 0,
                                format_column(option, self.rightmost, alignment=alignment),
                                curses.A_BOLD)
            else:
                self.pad.addstr(line_number, 0,
                                format_column(option, self.rightmost, alignment=alignment),
                                )

    def refresh(self):
        if self.options:
            self.add_options()
        self.stdscr.noutrefresh()
        self.pad.noutrefresh(0, 0, 0, 0, self.bottom, self.rightmost)
        curses.doupdate()

    def add_help(self):
        self.add_left_string(self.bottom, 'hjkl to navigate',
                             curses.A_REVERSE)
        self.add_right_string(self.bottom, 'q to quit',
                              curses.A_REVERSE)
        self.bottom -= 1
        self.stdscr.refresh()

    def move_cursor_y(self, step):
        cursor_result = self.cursor_y + step
        if cursor_result > (len(self.options) - 1) or cursor_result < 0:
            pass
        else:
            self.cursor_y = cursor_result
            self.pad.move(self.cursor_y, self.cursor_x)

    def interact(self):
        while True:
            input_char = self.stdscr.getch()
            if input_char == ord('q'):
                break
            if input_char == ord('j'):
                self.move_cursor_y(1)
            if input_char == ord('k'):
                self.move_cursor_y(-1)
            if input_char == ord('o'):
                return self.options[self.cursor_y]
            self.refresh()

    def terminate(self):
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
