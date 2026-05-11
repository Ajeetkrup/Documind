from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from operator import add

class GraphRAGState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    query: str
    strategy: str
    retrieved_docs: List[str]
    graph_context: List[dict]
    relevant_score: str
    iteration_count: int
    thinking: str
    answer: str
