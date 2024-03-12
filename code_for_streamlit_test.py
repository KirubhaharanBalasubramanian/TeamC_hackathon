# Import required libraries
import json
import vertexai
from operator import itemgetter
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatVertexAI
from langchain.llms import VertexAI
from langchain.schema.vectorstore import VectorStoreRetriever
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.callbacks.tracers import ConsoleCallbackHandler
from google.cloud import bigquery
from langchain_core.output_parsers import StrOutputParser

import google.auth

credentials, project_id = google.auth.default()

# Vertex configuration
VERTEX_PROJECT = "teamc-416909"
VERTEX_REGION = "us-central1"

# BigQuery configuration
BIGQUERY_DATASET = "hackathon"
BIGQUERY_PROJECT = "teamc-416909"

# Initialize Vertex AI
vertexai.init(project=VERTEX_PROJECT, location=VERTEX_REGION)

# Get BigQuery tables and schemas
bq_client = bigquery.Client(project=VERTEX_PROJECT)
bq_tables = bq_client.list_tables(dataset=f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}")
schemas = []

for bq_table in bq_tables:
    t = bq_client.get_table(f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{bq_table.table_id}")
    schema_fields = [f.to_api_repr() for f in t.schema]
    schema = f"The schema for table {bq_table.table_id} is the following: \n```{json.dumps(schema_fields, indent=1)}```"
    schemas.append(schema)

print(f"Found {len(schemas)} tables in dataset {BIGQUERY_PROJECT}:{BIGQUERY_DATASET}")

# Initialize vector store
embeddings = VertexAIEmbeddings()
vector_store = None

try:
    # Avoid duplicated documents by deleting the collection
    if vector_store:
        vector_store.delete_collection()
except Exception as e:
    print(f"Error while deleting collection: {e}")
else:
    print("Collection 'vector_store' deleted successfully.")

# Create a new Chroma object
vector_store = Chroma.from_texts(schemas, embedding=embeddings)
n_docs = len(vector_store.get()['ids'])
retriever = vector_store.as_retriever(search_kwargs={'k': 1})
print(f"The vector store has {n_docs} documents")

# Models
query_model = ChatVertexAI(model_name="codechat-bison", max_output_tokens=2048)
interpret_data_model = ChatVertexAI(max_output_tokens=2048)

# Get a SQL query chain
SQL_PROMPT = """
You are a SQL and BigQuery expert.
Your job is to create a query for BigQuery in SQL.
The following paragraph contains the schema of the table used for a query of all POIs in Paris. It is encoded in JSON format.

{context}

Create a BigQuery SQL query for the following user input, using the above table.
The user and the agent have done this conversation so far:
{chat_history}

Follow these restrictions strictly:
- Only return the SQL code.
- Do not add backticks or any markup (no code blocks). Only write the query as output. NOTHING ELSE.
- In FROM, always use the full table path, using `{project}` as project and `{dataset}` as dataset.
- Always transform country names to country codes (France = FR, Great Britain = GB)

User input: {question}

SQL query:
"""


# Get documents
def get_documents(retriever: VectorStoreRetriever, question: str) -> str:
    # Return only the first document
    output = ""
    for d in retriever.get_relevant_documents(question):
        output += d.page_content
        output += "\n"
        return output


# Exercise starts here
prompt_template = PromptTemplate(
    input_variables=["context", "chat_history", "question", "project", "dataset"],
    template=SQL_PROMPT)

partial_prompt = prompt_template.partial(project=BIGQUERY_PROJECT,
                                         dataset=BIGQUERY_DATASET)

docs = {"context": lambda x: get_documents(retriever, x['input'])}
question = {"question": itemgetter("input")}
chat_history = {"chat_history": itemgetter("chat_history")}
query_chain = docs | question | chat_history | partial_prompt | query_model
query = query_chain | StrOutputParser()
# Exercise ends here

# Add more outputs to the previous chain
query_response_schema = [
    ResponseSchema(name="query", description="SQL query to solve the user question."),
    ResponseSchema(name="question", description="Question asked by the user."),
    ResponseSchema(name="context", description="Documents retrieved from the vector store.")
]

#query_output_parser = StructuredOutputParser.from_response_schemas(query_response_schema)
# = docs | question | {"query": query} | RunnableLambda(lambda x: "```\n" + json.dumps(x) + "\n```") | StructuredOutputParser()
#query_output = query_output_json | query_output_parser
q_output = query_response_schema

# Interpret the output chain
INTERPRET_PROMPT = """You are a BigQuery expert. You are also expert in extracting data from CSV.

The following paragraph describes the schema of the table used for a query. It is encoded in JSON format.

{context}

A user asked this question:
{question}

To find the answer, the following SQL query was run in BigQuery:
```
{query}
```

The result of that query was the following table in CSV format:
```
{result}
```

Based on those results, provide a brief answer to the user question.

Follow these restrictions strictly:
- Do not add any explanation about how the answer is obtained, just write the answer.
- Extract any value related to the answer only from the result of the query. Do not use any other data source.
- Just write the answer, omit the question from your answer, this is a chat, just provide the answer.
- If you cannot find the answer in the result, do not make up any data, just say "I cannot find the answer"
"""


# Get BigQuery CSV
def get_bq_csv(bq_client: bigquery.Client, query: str) -> str:
    df = bq_client.query(query, location="US").to_dataframe()
    return df.to_csv(index=False)


# Exercise starts here
query = {"query": itemgetter("query")}
context = {"context": itemgetter("context")}
question = {"question": itemgetter("question")}
query_result = {"result": lambda x: get_bq_csv(bq_client, '\n'.join(x["query"].split('\n')[1:-1]))}

prompt = PromptTemplate(
    input_variables=["question", "query", "result", "context"],
    template=INTERPRET_PROMPT)

run_bq_chain = context | question | query | query_result | prompt
run_bq_result = run_bq_chain | interpret_data_model | StrOutputParser()
# Exercise ends here

def interpret_data_model(message):
    x = {"input": message, "chat_history": ""}
    return (run_bq_result.invoke(q_output.invoke(x)))
