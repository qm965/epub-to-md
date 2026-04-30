class EpubToMdError(Exception):
    """Base exception for epub-to-md conversion errors."""


class InvalidEpubError(EpubToMdError):
    """Raised when the input file is not a valid EPUB."""


class MissingMetadataError(EpubToMdError):
    """Raised when required metadata is missing."""
