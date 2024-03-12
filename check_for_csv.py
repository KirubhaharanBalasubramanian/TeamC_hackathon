# check if file exists in a gcs bucket, if yes put content in string, else wait 5 sec and retry
from io import BytesIO

from google.cloud import storage
import time
import pandas as pd


storage_client = storage.Client()
bucket_name = "teamc-hackathon"
blob_name = "output.csv"

while True:
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        file_contents = blob.download_as_text()
        blob_file = BytesIO(file_contents.encode())
        df = pd.read_csv(blob_file, sep=';')
        print(df)
        print("File found! File contents:", file_contents)
        break
    except Exception as e:
        print(f"File not found, checking again in 5 seconds... {e}")
        time.sleep(5)

print("End of script")
