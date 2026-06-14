class ManagerException(Exception):
    """
    thrown by classes that manage data,
    so that no matter if they use postgres or sqlite or anything else, business logic can handle it all the same way
    """
    pass