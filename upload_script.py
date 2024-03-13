# upload a file to a gcs bucket
#
from google.cloud import storage


def upload_drive(message):
    storage_client = storage.Client()
    bucket_name = "teamc-hackathon"
    blob_name = "input.txt"
    file_contents = message

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(file_contents)
    print("File uploaded")
