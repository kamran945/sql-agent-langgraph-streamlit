from typing import Annotated, Literal

from langchain_core.messages import AIMessage, ToolMessage

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages
from langchain_community.agent_toolkits import create_sql_agent

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

from src.state import GraphState
from src.chains import (
    query_checker_chain,
    query_generator_chain,
    get_schema_chain,
    sql_agent_exec,
    table_chain,
    final_answer_chain,
)
from src.llm import llm
from src.tools import db


def sql_agent(state: GraphState):
    print("--- sql_agent ----")
    response = sql_agent_exec.invoke({"input": state["messages"][-1].content})
    print(f"response: {response}")
    return {"messages": [AIMessage(content=response["output"])]}


def first_tool_call(state: GraphState) -> dict[str, list[AIMessage]]:
    print("---- first_tool_call ----")

    # print(f"{state['messages']}")
    # table_names = table_chain.invoke(state["messages"])
    # print(table_names)
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "sql_db_list_tables",
                        "args": {},
                        "id": "tool_xyz123",
                    }
                ],
            )
        ],
        "question": state["messages"][-1].content,
    }


def get_schema(state: GraphState) -> dict[str, list[AIMessage]]:
    print("---- get_schema ----")
    return {"messages": [get_schema_chain.invoke(state["messages"])]}


def correct_query(state: GraphState) -> dict[str, list[AIMessage]]:
    """
    Utilize this tool to verify the accuracy of your query before executing it.
    """
    print("---- correct_query ----")
    return {
        "messages": [query_checker_chain.invoke({"messages": [state["messages"][-1]]})]
    }


def generate_query(state: GraphState):
    print("---- generate_query ----")
    print(f"STATE: {state}")
    message = query_generator_chain.invoke(state)

    tool_messages = []
    if message.tool_calls:
        for tc in message.tool_calls:
            if tc["name"] != "SubmitFinalAnswer":
                print(f"Error: The wrong tool was called: {tc['name']}.")
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tc['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tc["id"],
                    )
                )
    else:
        tool_messages = []
    return {"messages": [message] + tool_messages}


def give_final_answer(state: GraphState):
    print("---- give_final_answer ----")
    return {
        "messages": [
            final_answer_chain.invoke(
                {
                    "question": state["question"],
                    "sql_result": state["messages"][-1].tool_calls[-1]["args"][
                        "final_answer"
                    ],
                }
            )
        ]
    }
