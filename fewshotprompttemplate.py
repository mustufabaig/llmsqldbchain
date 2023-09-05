from langchain import FewShotPromptTemplate

# create our examples
examples = [
  {
    "Question" : "How I compare against my peers in fraud performance?",
    "SQLQuery" : "SELECT a.industry_description as industry, a.region_description as region, sum(a.fraud_amount_usd) as my_fraud_volume_in_usd, sum(b.fraud_amount_usd) as my_peers_fraud_volume_in_usd \
FROM my_me_benchmark a \
    JOIN my_peer_benchmark b on a.parent_aggregate_merchant_id = b.parent_aggregate_merchant_id \
WHERE a.parent_aggregate_merchant_id = 10000111 \
      and a.industry_description = b.industry_description \
      and a.region_description = b.region_description \
group by a.industry_description, a.region_description \
order by a.industry_description, a.region_description",
    "SQLResult" : [
      ('Automotive Fuel', 'ASIA/PACIFIC', 653.85, 26963.5),
      ('Automotive Fuel', 'CANADA', 59011.8, 2390928.45),
      ('Automotive Fuel', 'EUROPE', 13815.1, 407002.7),
      ('Wholesale Clubs', 'MIDDLE EAST/AFRICA', 0, 1765112.2),
      ('Wholesale Clubs', 'UNITED STATES', 3007841.2, 8445211.55)
    ]
  }
]

# create a example template
example_template = """
Question: {Question}
SQLQuery: {SQLQuery}
SQLResult: {SQLResult}
"""

# create a prompt example from above template
example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult"],
    template=example_template
)

# now break our previous prompt into a prefix and suffix
# the prefix is our instructions
prefix = """Answer the question based on the context below. If the question cannot be answered using the information provided answer with "I don't know". 
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

Here are some examples:
"""

# and the suffix our user input and output indicator
suffix = """Question: {input}"""

# now create the few shot prompt template
few_shot_prompt_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input"],
    example_separator="\n\n"
)
