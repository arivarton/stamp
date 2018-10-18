import sys


def db_commit_decorator(func):
    def wrapper(args):
        x = func(args)
        args.db.commit()
        return x
    return wrapper

def no_db_no_action_decorator(func):
    def wrapper(args):
        if args.db.new_db:
            print('This action cannot be run before the selected database is populated!\n' \
                  'Selected database: %s\n' \
                  'Run `stamp add` to populate the database or select a different database with the --db argument.'
                  % (args.db + '.db'))
            sys.exit(0)
        return func(args)
    return wrapper
