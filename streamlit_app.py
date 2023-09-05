import streamlit as st
import json

from langchain import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate
from langchain import FewShotPromptTemplate

import fewshotprompttemplate as fspt

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
# now create the few shot prompt template
few_shot_prompt_template = FewShotPromptTemplate(
    examples=fspt.examples,
    example_prompt=fspt.example_prompt,
    prefix=fspt.prefix,
    suffix=fspt.suffix,
    input_variables=["input", "table_info", "dialect"],
    example_separator="\n\n"
)

db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=few_shot_prompt_template, verbose=True, top_k=3, use_query_checker=True, return_intermediate_steps=True)

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
