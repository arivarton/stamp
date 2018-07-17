import sys
import tty
import termios
from .helpers import get_terminal_width
from .exceptions import CanceledByUser


def yes_or_no(question,
              yes_message=None,
              yes_function=None, yes_function_args=None, yes_function_kwargs=None,
              no_message=None,
              no_function=None, no_function_args=None, no_function_kwargs=None):

    yes_function_args = yes_function_args or ()
    yes_function_kwargs = yes_function_kwargs or {}
    no_function_args = no_function_args or ()
    no_function_kwargs = no_function_kwargs or {}

    while True:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            print(question + ' [Y/n]')
            tty.setcbreak(fd)
            user_choice = sys.stdin.read(1)
        except KeyboardInterrupt:
            raise CanceledByUser
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if user_choice.lower() in ['y', '\n']:
            if yes_message:
                print(yes_message)
            return yes_function(*yes_function_args, **yes_function_kwargs) or None

        elif user_choice.lower() in ['n']:
            if no_message:
                print(no_message)
            return no_function(*no_function_args, **no_function_kwargs) or None

        else:
            print('\'%s\' is not a recognised answer!' % user_choice)


def provide_input(provision_type):
    try:
        print('Provide', provision_type + ':')
        user_input = input()
        if not user_input:
            print('No', provision_type, 'provided!')
            print('Canceling...')
            sys.exit(0)
        else:
            return user_input
    except KeyboardInterrupt:
        print('\nCanceling...')
        sys.exit(0)


def value_for(value_name):
    try:
        print('Value for', value_name + ':')
        user_input = input()
        if not user_input:
            return None
        else:
            return user_input
    except KeyboardInterrupt:
        print('\nCanceling...')
        sys.exit(0)


def divider(divider_type='-', alignment='<', text=''):
    return '{0:{divider_type}{alignment}{width}}'.format(text,
                                                         divider_type=divider_type,
                                                         alignment=alignment,
                                                         width=get_terminal_width())


def format_column(text, width, alignment='^'):
    return '{0:{alignment}{width}}'.format(text, alignment=alignment, width=width)
