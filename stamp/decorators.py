def db_commit_decorator(func):
    def wrapper(args):
        func(args)
        args.db.commit()
    return wrapper
