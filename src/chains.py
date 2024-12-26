from langchain_community.agent_toolkits import create_sql_agent
from typing import List
from operator import itemgetter
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


from src.prompts import (
    query_checker_prompt,
    query_generator_prompt,
    category_system_prompt,
    category_prompt,
    final_answer_prompt,
)
from src.llm import llm
from src.tools import db_query_tool, get_schema_tool
from src.schema import SubmitFinalAnswer
from src.schema import Table, Tables
from src.db import db


from langchain.chains.openai_tools import create_extraction_chain_pydantic


def get_table_names(tables: List[Table]) -> List[str]:
    return [table.name for table in tables]


# category_chain = create_extraction_chain_pydantic(
#     pydantic_schemas=Table, llm=llm, system_message=category_system_prompt
# )
# table_chain = {"input": itemgetter("question")} | category_chain | get_table_names
table_chain = category_prompt | llm.with_structured_output(schema=Tables)


query_checker_chain = query_checker_prompt | llm.bind_tools(
    [db_query_tool], tool_choice="required"
)

get_schema_chain = llm.bind_tools([get_schema_tool])

query_generator_chain = query_generator_prompt | llm.bind_tools([SubmitFinalAnswer])

final_answer_chain = final_answer_prompt | llm


sql_agent_exec = create_sql_agent(llm, db=db, agent_type="tool-calling", verbose=False)
