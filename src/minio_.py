import numpy as np
from PIL import Image
from io import BytesIO
from minio import Minio
from typing import NamedTuple
from minio.error import BucketAlreadyOwnedByYou


class MinioConfig(NamedTuple):
    endpoint: str = '127.0.0.1:9000'
    access_key: str = 'minioadmin'
    secret_key: str = 'minioadmin'
    secure: bool = False


def handle_minio_errors():
    ...


class MinioClient:

    def __init__(self, config=MinioConfig()):
        self.minio_client = Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure
        )

    def create_bucket(self, bucket_name: str):
        # Todo: use decorator to handle minio errors
        try:
            self.minio_client.make_bucket(bucket_name=bucket_name, location="us-east-1")
        except BucketAlreadyOwnedByYou as err:
            pass

    def upload_image(self, bucket_name: str, object_name: str, file_path: str):
        self.minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type='image/jpg'
        )

    def download_image(self, bucket_name: str, object_name: str, file_path: str):
        stat = self.minio_client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path
        )

    def get_image(self, bucket_name: str, object_name: str) -> np.ndarray:
        try:
            response = self.minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
            return np.asarray(Image.open(BytesIO(response.read())))
        except Exception as e:
            print(e)
        finally:
            response.close()
            response.release_conn()

    def list_objects(self, bucket_name: str):
        objects = self.minio_client.list_objects(
            bucket_name=bucket_name,
            recursive=True
        )
        for obj in objects:
            yield obj.object_name

if __name__ == '__main__':
    import os
    import matplotlib.pyplot as plt

    mc = MinioClient()
    kipyatcom = 'kipyatcom'
    mc.create_bucket(bucket_name=kipyatcom)
    # events = '../data/imgs/events'
    # for event in os.listdir(events):
    #     for image in os.listdir(os.path.join(events, event)):
    #         fp = os.path.join(events, event, image)
    #         mc.put_image(bucket_name=kipyatcom, object_name=f'{event}/{image}', file_path=fp)

    # arr = mc.get_image(bucket_name=kipyatcom, object_name='36948/KIPYATCOM_222.jpg')
    # plt.imshow(arr)
    # plt.show()
