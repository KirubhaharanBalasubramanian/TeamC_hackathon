import streamlit as st
from google.cloud import bigquery
from code_for_streamlit_test import interpret_data_model

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

    # try:
    #   data = fetch_bigquery_data()
    #   st.table(data)

    # except Exception as e:
    #  st.error(f"Error: {str(e)}")

    user_input = st.text_input("Enter your query:")

    if st.button("Submit"):
        try:
            st.write(interpret_data_model(user_input))

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
