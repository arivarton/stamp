def yes_or_no(question,
              no_message=None,
              no_function=None, no_function_args=(), no_function_kwargs={},
              yes_message=None,
              yes_function=None, yes_function_args=(), yes_function_kwargs={}):
    try:
        user_choice = input(question + ' [Y/n] ')
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
