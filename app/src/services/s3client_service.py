import boto3
from exceptions import S3ClientException

class S3ClientService:
    """
    A simple S3 client to interact with AWS S3 buckets.
    This client provides methods to get objects from a specified S3 bucket.
    """
    bucket: str = None
    __client: boto3.client = None

    def __init__(self, bucket: str = None):
        """
        Initializes the S3Client with the specified bucket name.
        :param bucket: The name of the S3 bucket to interact with.
        """
        self.bucket = bucket
        self.__client = boto3.client('s3')

    def get_object(self, key: str):
        try:
            response = self.__client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            return response
        except Exception as e:
            raise S3ClientException(f"Getting object {key} from bucket {self._bucket}: {e}") from e