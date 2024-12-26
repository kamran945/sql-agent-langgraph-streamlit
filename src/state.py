from langgraph.graph import MessagesState


class GraphState(MessagesState):
    question: str = ""
