from exceptions.base_exception import BaseException

class S3ClientException(BaseException):
    """Base exception for S3 client errors."""
    _title = "S3 Client Exception"