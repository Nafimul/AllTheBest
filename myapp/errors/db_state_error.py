class DbStateError(Exception):
    """
    for when an operation can't be done on the db
    because of something like a unique constraint for example
    """
    pass