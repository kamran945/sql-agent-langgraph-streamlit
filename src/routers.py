from typing import Literal
from langgraph.graph import END

from src.state import GraphState


def should_continue(
    state: GraphState,
) -> Literal["correct_query", "generate_query", "give_final_answer"]:
    messages = state["messages"]
    last_message = messages[-1]

    if getattr(last_message, "tool_calls", None):
        return "give_final_answer"
    if last_message.content.startswith("Error:"):
        return "generate_query"
    else:
        return "correct_query"
