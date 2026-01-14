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


class MaximumSectionDepthException(FPConvertException):
    """Raised when a section being constructed crosses maximum allowed depth."""

    pass


class MissingHeaderException(FPConvertException):
    """Raised when an expected header-item is not found in a node for table."""

    pass


class MissingNodeException(FPConvertException):
    """Raised when one or more expected nodes are not found in a mindmap."""

    pass
class MissingValueException(FPConvertException):
    """Raised when an expected column-value is not found in a node for table."""

    pass


class InvalidParameterException(FPConvertException):
    """Raised when an invalid parameter is supplied."""

    pass

class InvalidNodeException(FPConvertException):
    """Raised when an invalid node is supplied."""

    pass


class InvalidAttributeException(FPConvertException):
    """Raised when the value of an invalid attribute is sought."""

    pass
    """Raised when an invalid node is found at a particular location."""

    pass


class InvalidTypeException(FPConvertException):
    """Raised when an invalid type-values is found somewhere."""

    pass


class InvalidFPCBlockTypeException(FPConvertException):
    """Raised when an invalid or unsupported block-type-values is used."""

    pass

class InvalidFilePathException(FPConvertException):
    """Raised when an invalid or no file-path is supplied."""

    pass

class MissingPermissionException(FPConvertException):
    """Raised when required permission is missing to do something."""

    pass

class FileConversionException(FPConvertException):
    """Raised when a file conversion operation fails."""

    pass