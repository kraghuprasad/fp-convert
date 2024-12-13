
"""
Custom exceptions for the fp-convert package.
"""


class FPConvertException(Exception):
    """Base exception class for fp-convert package."""

    pass


class IncorrectInitialization(FPConvertException):
    """Object was initialized incorrectly."""

    pass


class InvalidRefException(FPConvertException):
    """Raised when a reference is invalid or cannot be resolved."""

    pass


class InvalidRefTypeException(FPConvertException):
    """Raised when a reference type is not supported or invalid."""

    pass


class MissingFileException(FPConvertException):
    """Raised when a required file is missing."""

    pass


class UnsupportedFileException(FPConvertException):
    """Raised when the file type is not supported."""

    pass


class InvalidDocInfoKey(FPConvertException):
    """Raised when an invalid DocInfo key is supplied to set value."""

    pass


class MaximumListDepthException(FPConvertException):
    """Raised when a list being constructed crosses maximum allowed depth."""

    pass
