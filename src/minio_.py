import os
from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
from typing import NamedTuple


class MinioConfig(NamedTuple):
    endpoint: str = '127.0.0.1:9000'
    access_key: str = 'minioadmin'
    secret_key: str = 'minioadmin'
    secure: bool = False


class MinioClient:

    def __init__(self, config=MinioConfig()):
        self.minio_client = Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure
        )

    def create_bucket(self, bucket_name: str):
        try:
            self.minio_client.make_bucket(bucket_name=bucket_name, location="us-east-1")
        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            raise

    def put_image(self, bucket_name: str, object_name: str, file_path: str):
        try:
            self.minio_client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type='image/jpg'
            )
        except ResponseError as err:
            print(err)


if __name__ == '__main__':
    mc = MinioClient()
    kipyatcom_bucket = 'kipyatcom'
    mc.create_bucket(bucket_name=kipyatcom_bucket)
    events = '../data/imgs/events'
    for event in os.listdir(events):
        for image in os.listdir(os.path.join(events, event)):
            fp = os.path.join(events, event, image)
            mc.put_image(bucket_name=kipyatcom_bucket, object_name=f'{event}/{image}', file_path=fp)
