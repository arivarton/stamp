def db_commit_decorator(func):
    def wrapper(args):
        x = func(args)
        args.db.commit()
        return x
    return wrapper
