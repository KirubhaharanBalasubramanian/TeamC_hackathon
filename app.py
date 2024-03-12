import streamlit as st
from google.cloud import bigquery

# Set your Google Cloud Project ID
PROJECT_ID = "teamc-416909"

# Authenticate with Google Cloud for BigQuery
bigquery_client = bigquery.Client(project=PROJECT_ID)

# Set your BigQuery dataset and table
DATASET_ID = "hackathon"
TABLE_ID = "places"

# Streamlit app
def main():
    st.title("Hackathon Team C")

    try:
        # Fetch data from BigQuery
        data = fetch_bigquery_data()

        # Display data in a table
        st.table(data)

    except Exception as e:
        st.error(f"Error: {str(e)}")

def fetch_bigquery_data():
    # Construct the SQL query
    sql_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` LIMIT 100"

    # Execute the SQL query on BigQuery
    query_job = bigquery_client.query(sql_query)

    # Wait for the query job to complete
    results = query_job.result()

    # Extract and return the results
    result_list = []
    for row in results:
        result_list.append(dict(row.items()))

    return result_list


if __name__ == "__main__":
    main()
