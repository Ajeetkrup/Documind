from pydantic import BaseModel, Field
from src.utils.llm import qwen_llm
from src.utils.stream_events import emit_stream_event

class RouteDecision(BaseModel):
    strategy: str = Field(description="Must be 'semantic', 'graph', 'both', or 'direct'")

def route_query(state):
    emit_stream_event("node_start", name="Router")
    query = state.get("query")
    if not query and state.get("messages"):
        last_msg = state["messages"][-1]
        # Support both LangChain message objects and plain dicts
        query = getattr(last_msg, "content", None) or last_msg.get("content", "")

    router_llm = qwen_llm.with_structured_output(RouteDecision)
    prompt = f"""
    You are a legal query routing assistant.
    Analyze the user query to determine the best retrieval strategy only if required if the use is asking generic questions or not related to contract analysis, then only use 'direct' strategy:
    - 'direct': if the user is just saying hello, greeting, or asking a general conversational question that does not require document retrieval.
    - 'semantic': for general meaning, facts, or concepts.
    - 'graph': for dependencies, references, superseding documents, or conflicts.
    - 'both': if the query requires both specific facts and multi-hop relationships.
    Query: {query}
    """
    decision = router_llm.invoke(prompt)
    emit_stream_event("node_end", name="Router")
    return {"strategy": decision.strategy, "query": query}
