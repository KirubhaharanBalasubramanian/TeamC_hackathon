# upload a file to a gcs bucket
#
from google.cloud import storage

storage_client = storage.Client()
bucket_name = "teamc-hackathon"
blob_name = "user_input3.txt"
file_contents = "Hello World!"

bucket = storage_client.get_bucket(bucket_name)
blob = bucket.blob(blob_name)
blob.upload_from_string(file_contents)
print("File uploaded")
