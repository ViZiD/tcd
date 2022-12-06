__all__ = [
    "KeyDataBadDecryptedSize",
    "KeyDataBadChecksum",
    "KeyFileInvalidMagic",
    "CacheFileInvaildMagic",
    "KeyFileInvalidChecksum",
    "KeyFileNotFound",
    "LocalKeyInvalidChecksum",
    "DirNotExist",
    "FileNotExist",
]


class KeyDataBadDecryptedSize(Exception):
    """
    The decrypted data size part of the file is corrupted
    """


class KeyDataBadChecksum(Exception):
    """
    Could not decrypt the data with this key\n
    This usually mean that the file is password-encrypted
    """


class KeyFileInvalidMagic(Exception):
    """
    Key file has an invalid magic bytes
    """


class CacheFileInvaildMagic(Exception):
    """
    Cache has an invalid magic bytes
    """


class LocalKeyInvalidChecksum(Exception):
    """
    Wrong key
    """


class KeyFileInvalidChecksum(Exception):
    """
    Key file has an invalid checksum
    """


class KeyFileNotFound(Exception):
    """
    Key file not found
    """


class DirNotExist(Exception):
    """
    Directory not exists
    """


class FileNotExist(Exception):
    """
    File not exist
    """


class MissingArgumentError(Exception):
    """
    Base class for the missing required arguments events.
    """
