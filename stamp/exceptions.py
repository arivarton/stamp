class StampError(Exception):
    pass


class TagOutsideTimeBoundaryError(StampError):
    pass


class NoMatchingDatabaseEntryError(StampError):
    pass


class TooManyMatchingDatabaseEntriesError(StampError):
    pass


class TooManyMatchesError(StampError):
    pass


class NoMatchesError(StampError):
    pass


class NonExistingId(StampError):
    pass


class ArgumentError(StampError):
    pass


class CurrentStampNotFoundError(StampError):
    pass


class CanceledByUser(StampError):
    def __init__(self, message='Canceling...'):
        super().__init__(message)


class RequiredValueError(StampError):
    pass


class DeleteNotAllowedError(StampError):
    pass
