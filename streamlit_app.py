import streamlit as st
import json

from langchain import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate

#setting streamlit properties
st.set_page_config(layout="wide")

#loading config from streamlit settings
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
username = st.secrets["username"]
password = st.secrets["password"]
warehouse = st.secrets["warehouse"]
role = st.secrets["role"]
snowflake_account = st.secrets["account"]
database = st.secrets["database"]
schema = st.secrets["schema"]

# setup
snowflake_url = f"snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}"
db = SQLDatabase.from_uri(snowflake_url,sample_rows_in_table_info=3, include_tables=['merchant','my_me_benchmark','my_peer_benchmark'])
# llm = OpenAI(temperature=0) # using the following code to cache with gptcache
llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo', verbose=True)

#prompt template
_DEFAULT_TEMPLATE = """Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know". 

Context: Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer to the input question. 
Unless the user specifies in the question a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per {dialect}. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use sysdate() function to get the current date, if the question involves "today".
Always use parent_aggregate_merchant_id=10000111, industry_description = "Wholesale Clubs". 

Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}

If someone asks to compare data with peers then join my_me_benchmark table with my_peer_benchmark table and then compare the measures from both tables.
If someone mentions "performance" then they really mean "volume".

Question: {input}"""
PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
)

db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=PROMPT, verbose=True, top_k=3, use_query_checker=True, return_intermediate_steps=True)

question = st.chat_input("How can I help you?")
if question:
    st.markdown(":question: "+question)
    with st.spinner('Looking for answers...'):
        #answer = db_chain.run(question)
        answer = db_chain(question)
        with st.chat_message("assistant"):
            st.write("here is what I have found...")
            #st.info(answer);
            pretty_json = json.dumps(answer["intermediate_steps"], indent=4)
            st.code(answer["intermediate_steps"][5].replace("Final answer here:",""))
            #st.code(pretty_json, language="json", line_numbers=True)
        with st.expander("Click for generated SQL"):
            st.text(answer["intermediate_steps"][1])
