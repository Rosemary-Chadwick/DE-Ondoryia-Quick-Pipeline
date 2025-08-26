import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from minio import Minio
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA_BRONZE")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

files_to_ingest = [
    "faction_distribution.csv",
    "households.csv",
    #"language_building_blocks.csv",
    #"language_roots.csv",
    #"moons.csv",
    "people.csv",
    #"planets.csv",
    #"region_biome.csv",
    "regions.csv"
]

def main():
    minio_client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    snowflake_conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    print("Files in MinIO bucket:")
    objects = list(minio_client.list_objects(MINIO_BUCKET_NAME))
    for obj in objects:
        print(f"  - {obj.object_name}")

    for file_name in files_to_ingest:
        response = minio_client.get_object(MINIO_BUCKET_NAME, file_name)
        df = pd.read_csv(BytesIO(response.read()))

        table_name = file_name.replace('.csv', '')
        write_pandas(
            snowflake_conn, 
            df, 
            table_name=table_name,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            auto_create_table=True,
            overwrite=True
        )

    snowflake_conn.close()
    print("All files loaded successfully!")

if __name__ == "__main__":
    main()