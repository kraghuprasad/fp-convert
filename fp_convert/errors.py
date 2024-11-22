"""
Custom exceptions for the fp-convert package.
"""
from exceptions import BaseException


class IncorrectInitialization(BaseException):
    """
    Object was initialized incorrectly.
    """
    def __init__(self, message):
        raise message


class InvalidRefException(BaseException):
    """Raised when a reference is invalid or cannot be resolved."""
    def __init__(self, msg):
        super().__init__(msg)


class InvalidRefTypeException(BaseException):
    """Raised when a reference type is not supported or invalid."""
    def __init__(self, msg):
        super().__init__(msg)


class MissingFileException(BaseException):
    """Raised when a required file is missing."""
    def __init__(self, msg):
        super().__init__(msg)


class InvalidDocinfoKey(BaseException):
    """Raised when an invalid DocInfo key is supplied to set value."""
    def __init__(self, msg):
        super().__init__(msg)