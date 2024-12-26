from langgraph.graph import StateGraph, START, END


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


from src.state import GraphState
from src.nodes import (
    first_tool_call,
    get_schema,
    generate_query,
    correct_query,
    give_final_answer,
    sql_agent,
)
from src.tools import (
    list_tables_tool,
    get_schema_tool,
    create_tool_node_with_fallback,
    db_query_tool,
)
from src.routers import should_continue

workflow = StateGraph(GraphState)

# workflow.add_node("sql_agent", sql_agent)
# workflow.set_entry_point("sql_agent")
# workflow.add_edge("sql_agent", END)

workflow.add_node("first_tool_call", first_tool_call)
workflow.add_node(
    "list_tables_tool", create_tool_node_with_fallback([list_tables_tool])
)
workflow.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))
workflow.add_node("get_schema", get_schema)

workflow.add_node("generate_query", generate_query)
workflow.add_node("correct_query", correct_query)
workflow.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))
workflow.add_node("give_final_answer", give_final_answer)


workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "get_schema")
workflow.add_edge("get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "generate_query")
workflow.add_conditional_edges(
    "generate_query",
    should_continue,
)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "generate_query")

workflow.add_edge("give_final_answer", END)

graph = workflow.compile()
