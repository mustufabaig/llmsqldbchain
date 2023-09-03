import streamlit as st
from langchain import OpenAI, SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from gptcache.adapter.langchain_models import LangChainLLMs
from gptcache.session import Session
session = Session(name="sql-example") # set session for LangChainLLMs


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
username = st.secrets["username"]
password = st.secrets["password"]
warehouse = st.secrets["warehouse"]
role = st.secrets["role"]
snowflake_account = st.secrets["account"]
database = st.secrets["database"]
schema = st.secrets["schema"]

snowflake_url = f"snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}"
db = SQLDatabase.from_uri(snowflake_url,sample_rows_in_table_info=1, include_tables=['merchant','my_me_merchant_benchmark','my_peer_merchant_benchmark','my_region_merchant_benchmark'])
# llm = OpenAI(temperature=0) # using the following code to cache with gptcache
llm = LangChainLLMs(llm=OpenAI(temperature=0), session=session)

db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

