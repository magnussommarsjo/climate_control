class ControllerError(Exception):
    pass

class NotWritableError(ControllerError):
    pass