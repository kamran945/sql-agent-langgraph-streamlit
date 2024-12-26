from langchain_core.prompts import ChatPromptTemplate
from src.schema import SubmitFinalAnswer
from src.db import db

category_system_prompt = f"""Return the names of the SQL tables that are relevant to the user question.
The tables are:

{", ".join(db.get_usable_table_names())}
"""
category_prompt = ChatPromptTemplate(
    [("system", category_system_prompt), ("placeholder", "{messages}")]
)

query_checker_system_prompt = """You are a SQL expert with a strong attention to detail.
Double check the SQLite query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

You will call the appropriate tool to execute the query after running this check."""

query_checker_prompt = ChatPromptTemplate(
    [("system", query_checker_system_prompt), ("placeholder", "{messages}")]
)
"""Given an input question, create a syntactically correct {dialect} query to run to help find the answer. 
Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. 
However, if the user's question implies that all relevant entries should be retrieved (e.g., asking for "all customers", "all records", "every instance", etc.), do not apply any limit on the results. Focus on retrieving all relevant entries in such cases.
You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Only use the following tables:
{table_info}

Question: {input}"""
query_generator_system_prompt = """You are a SQL expert with a strong attention to detail.

Given an input question, output syntactically correct SQLite queries to run, then look at the results of the queries and return the answer.

DO NOT call any tool besides SubmitFinalAnswer to submit the final answer.

When generating the query:
Output the SQL query that answers the input question without a tool call.
Only use the following tables:
{table_info}

Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.

If you get an error while executing a query, rewrite the query and try again.

If you get an empty result set, you should try to rewrite the query to get a non-empty result set. 
NEVER make stuff up if you don't have enough information to answer the query... just say you don't have enough information.

If you have enough information to answer the input question, simply invoke the appropriate tool to submit the final answer to the user.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database."""

query_generator_prompt = ChatPromptTemplate(
    [("system", query_generator_system_prompt), ("placeholder", "{messages}")]
).partial(table_info=db.get_table_info())

final_answer_system_prompt = """You are an expert database assistant. 
Given a user question and the SQL query result, respond naturally, mentioning the question in as few words as possible and giving the answer clearly and directly. 
Be precise and to the point.
Question: {question}
SQL Result: {sql_result}
Start the answer """
final_answer_prompt = ChatPromptTemplate([("system", final_answer_system_prompt)])
