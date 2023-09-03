import streamlit as st
from langchain import OpenAI, SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
username = st.secrets["username"]
password = st.secrets["password"]
warehouse = st.secrets["warehouse"]
role = st.secrets["role"]
snowflake_account = st.secrets["account"]
database = st.secrets["database"]
schema = st.secrets["schema"]

snowflake_url = f"snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}"
db = SQLDatabase.from_uri(snowflake_url,sample_rows_in_table_info=1, include_tables=['merchant'])
# llm = OpenAI(temperature=0) # using the following code to cache with gptcache
llm = OpenAI(temperature=0, verbose=True)

db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

db_chain.run("How many employees are there?")
