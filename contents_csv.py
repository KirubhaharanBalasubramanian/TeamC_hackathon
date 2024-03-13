from io import BytesIO
from google.cloud import storage
import time
import pandas as pd


def contents_from_CSV():
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
            df.to_csv("/Users/kirubha/Documents/GitHub/TeamC_hackathon/csv/local_output.csv", index=False,  sep=';')
            print(f"DataFrame saved locally as local_output.csv")
            blob.delete()
            return(df)
        except Exception as e:
            print(f"File not found, checking again in 5 seconds... {e}")
            time.sleep(5)



