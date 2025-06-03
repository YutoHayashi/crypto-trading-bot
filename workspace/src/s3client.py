import boto3
from exceptions.s3client_exception import S3ClientException

class S3Client:
    """
    A simple S3 client to interact with AWS S3 buckets.
    This client provides methods to get objects from a specified S3 bucket.
    """
    _bucket: str = ''
    __client: boto3.client = None

    def __init__(self, bucket: str):
        """
        Initializes the S3Client with the specified bucket name.
        :param bucket: The name of the S3 bucket to interact with.
        """
        self._bucket = bucket
        self.__client = boto3.client('s3')
    
    def get_object(self, key: str):
        try:
            response = self.__client.get_object(
                Bucket=self._bucket,
                Key=key
            )
            return response
        except Exception as e:
            raise S3ClientException(f"Getting object {key} from bucket {self._bucket}: {e}") from e