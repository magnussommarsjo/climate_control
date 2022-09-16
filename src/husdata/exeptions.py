class ControllerError(Exception):
    pass

class NotWritableError(ControllerError):
    pass

class TypeError(ControllerError):
    pass