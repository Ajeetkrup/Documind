from pydantic import BaseModel, Field
from src.utils.llm import qwen_llm
from src.utils.stream_events import emit_stream_event


class Grade(BaseModel):
    relevance: str = Field(description="'high' if context answers the query, else 'low'")
    reasoning: str


def grade_documents(state):
    emit_stream_event("node_start", name="Grade Documents")
    query = state["query"]
    docs = state.get("retrieved_docs", [])
    graph = state.get("graph_context", [])

    grader = qwen_llm.with_structured_output(Grade)
    prompt = f"""
    Assess if the retrieved context contains enough information to answer the query.
    Query: {query}
    Vector Context: {docs}
    Graph Context: {graph}
    """
    grade = grader.invoke(prompt)
    iteration = state.get("iteration_count", 0) + 1
    emit_stream_event("node_end", name="Grade Documents")
    return {"relevant_score": grade.relevance, "iteration_count": iteration}


def check_relevance(state):
    score = state.get("relevant_score", "low")
    iteration = state.get("iteration_count", 0)
    if score == "high" or iteration >= 3:
        return "generate"
    return "rewrite"


def rewrite_query(state):
    emit_stream_event("node_start", name="Rewrite Query")
    query = state["query"]
    prompt = f"Rewrite this query to be more specific and improve retrieval: {query}"
    new_query = qwen_llm.invoke(prompt).content
    emit_stream_event("node_end", name="Rewrite Query")
    return {"query": new_query}
