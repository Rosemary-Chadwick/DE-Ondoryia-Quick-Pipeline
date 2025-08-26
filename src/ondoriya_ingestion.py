import os
import requests
from minio import Minio
from io import BytesIO 
from dotenv import load_dotenv

load_dotenv()

FILES_TO_INGEST = os.getenv("FILES_TO_INGEST").split(",")

def main():
    minio_client = Minio(
        os.getenv("MINIO_URL"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False
    )

    for file_name in FILES_TO_INGEST:
            file_url = f"{os.getenv('ONDORIYA_API_URL')}/{file_name}"
            response = requests.get(file_url)
            response.raise_for_status()

            file_data = BytesIO(response.content)
            file_size = len(response.content)

            minio_client.put_object(
                os.getenv("MINIO_BUCKET_NAME"),
                file_name,
                file_data,
                file_size
            )

    print("Files ingested successfully.")

if __name__ == "__main__":
    main()