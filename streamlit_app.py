import streamlit as st
import json

from langchain import OpenAI, SQLDatabase
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
llm = OpenAI(temperature=0, model_name='gpt-3.5-turbo', verbose=True)

#prompt template
_DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}

If someone asks to compare data then comparative numbers will come from my_peer_benchmark table.
Always use parent_aggregate_merchant_id=10000111
Always aggregate

Question: {input}"""
PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
)

db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=PROMPT, verbose=True, top_k=3, return_intermediate_steps=True)

question = st.chat_input("How can I help you?")
if question:
    with st.spinner('Looking for answers...'):
        #answer = db_chain.run(question)
        answer = db_chain(question)
        with st.chat_message("assistant"):
            st.write("here is what I have found...")
            #st.info(answer);
            pretty_json = json.dumps(answer["intermediate_steps"], indent=4)
            st.code(pretty_json, language="json", line_numbers=True)
