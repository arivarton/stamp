class StampError(Exception):
    pass


class TagOutsideTimeBoundaryError(StampError):
    pass


class NoMatchingDatabaseEntryError(StampError):
    pass
