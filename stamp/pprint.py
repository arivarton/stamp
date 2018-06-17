from .helpers import get_terminal_width


def yes_or_no(question,
              no_message=None,
              no_function=None, no_function_args=(), no_function_kwargs={},
              yes_message=None,
              yes_function=None, yes_function_args=(), yes_function_kwargs={}):
    try:
        print(question + ' [Y/n]')
        user_choice = input()
    except KeyboardInterrupt:
        user_choice = 'n'
        if no_message:
            no_message = '\n' + no_message

    if user_choice.lower() in ['y', '']:
        if yes_message:
            print(yes_message)
        if yes_function:
            return yes_function(*yes_function_args, **yes_function_kwargs)
        else:
            return None

    else:
        if no_message:
            print(no_message)
        if no_function:
            return no_function(*no_function_args, **no_function_kwargs)
        else:
            return None


def divider(divider_type='-', alignment='<', text=''):
    print('{0:{divider_type}{alignment}{width}}'.format(text,
                                                        divider_type=divider_type,
                                                        alignment=alignment,
                                                        width=get_terminal_width()))
