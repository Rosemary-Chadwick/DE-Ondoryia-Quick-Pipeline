import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_url = os.getenv("MINIO_EXTERNAL_URL")
minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")

def create_bucket():
    try:
        minio_client = Minio(
            minio_url,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False,
        )
        if minio_client.bucket_exists(minio_bucket_name):
            print(f"Bucket '{minio_bucket_name}' already exists")
        else:
            minio_client.make_bucket(minio_bucket_name)
            print(f"Bucket '{minio_bucket_name}' created successfully")
            
    except Exception as e:
        print(f"Error creating bucket: {e}")

if __name__ == "__main__":
    create_bucket()