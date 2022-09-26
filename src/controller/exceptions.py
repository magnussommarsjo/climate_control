"""
Custom exceptions for the controller package
"""

class StrategyError(Exception):
    pass

class AlreadyRegisteredError(StrategyError):
    pass