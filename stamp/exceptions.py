class StampError(Exception):
    pass


class TagOutsideTimeBoundaryError(StampError):
    pass


class NoMatchingDatabaseEntryError(StampError):
    pass


class TooManyMatchesError(StampError):
    pass


class ArgumentError(StampError):
    pass
