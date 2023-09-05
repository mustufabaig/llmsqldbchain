from langchain import FewShotPromptTemplate

# create our examples
examples = [
  {
    "Question" : "How I compare against my peers in fraud performance?",
    "SQLQuery" : "SELECT a.industry_description as industry, a.region_description as region, sum(a.fraud_amount_usd) as my_fraud_volume_in_usd, sum(b.fraud_amount_usd) as my_peers_fraud_volume_in_usd
FROM my_me_benchmark a
    JOIN my_peer_benchmark b on a.parent_aggregate_merchant_id = b.parent_aggregate_merchant_id
WHERE a.parent_aggregate_merchant_id = 10000111
      and a.industry_description = b.industry_description
      and a.region_description = b.region_description
group by a.industry_description, a.region_description
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
Question: {query}
SQLQuery: {SQLQuery}
SQLResult: {SQLResult}
"""

# create a prompt example from above template
example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult"],
    template=example_template
)

prefix = """ """
suffix = """ """

