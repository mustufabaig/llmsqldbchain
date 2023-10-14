import streamlit as st
import json

from pprint import pprint
from langchain import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate
from langchain import FewShotPromptTemplate

import fewshotprompttemplate

#setting streamlit properties
st.set_page_config(layout="wide")

def get_db_chain():
    if 'db_chain' not in st.session_state:
        #st.write('dbchain was not in the session')
        #loading config from streamlit settings
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        OPENAI_API_BASE = st.secrets["OPENAI_API_BASE"]
        OPENAI_API_TYPE = st.secrets["OPENAI_API_TYPE"]
        OPENAI_API_VERSION = st.secrets["OPENAI_API_VERSION"]
        OPENAI_CHAT_MODEL = st.secrets["OPENAI_CHAT_MODEL_35"]
        MODEL_DEPLOYMENT_NAME = st.secrets["MODEL_DEPLOYMENT_NAME_35"]
        
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
        #llm = OpenAI(temperature=0) # using the following code to cache with gptcache
        #llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo', verbose=True)
        llm = AzureChatOpenAI(temperature=0, deployment_name=MODEL_DEPLOYMENT_NAME, model=OPENAI_CHAT_MODEL, verbose=True)
        
        #prompt template
        # now create the few shot prompt template
        few_shot_prompt_template = FewShotPromptTemplate(
            examples=fewshotprompttemplate.examples,
            example_prompt=fewshotprompttemplate.example_prompt,
            prefix=fewshotprompttemplate.prefix,
            suffix=fewshotprompttemplate.suffix,
            input_variables=["input", "table_info", "dialect"],
            example_separator="\n\n"
        )
        
        local_db_chain = SQLDatabaseChain(llm=llm, database=db, prompt=few_shot_prompt_template, verbose=True, top_k=3, use_query_checker=True, return_intermediate_steps=True)
        st.session_state['db_chain'] = local_db_chain
        return local_db_chain
        
    return st.session_state['db_chain']

db_chain = get_db_chain()

question = st.chat_input("How can I help you?")
if question:
    st.markdown(":question: "+question)
    with st.spinner('Looking for answers...'):
        #answer = db_chain.run(question)
        try:
            answer = db_chain(question)
            with st.chat_message("assistant"):
                st.write("here is what I have found...")
                #st.info(answer);
                pretty_json = json.dumps(answer["intermediate_steps"], indent=4)
                st.code(answer["intermediate_steps"][5].replace("Final answer here:",""))
                #st.code(pretty_json, language="json", line_numbers=True)
            with st.expander("Click here for details"):
                #st.text(answer["intermediate_steps"][1])
                st.text(json.dumps(answer["intermediate_steps"], indent=4))
        except Exception as error:
            with st.chat_message("assistant"):
                st.write("I don't think I can answer your question - try a different question.")
                with st.expander("Click here for more details"):
                    #st.write(vars(error))
                    st.text(json.dumps(error.intermediate_steps, indent=4))
