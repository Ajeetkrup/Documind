import re
from langchain_core.messages import AIMessage
from src.utils.llm import qwen_llm
from src.utils.stream_events import emit_stream_event


def _split_thinking(raw: str) -> tuple[str, str]:
    """Extract <think>...</think> block and return (thinking, answer)."""
    match = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
    if match:
        thinking = match.group(1).strip()
        answer = raw[match.end():].strip()
    else:
        thinking = ""
        answer = raw.strip()
    return thinking, answer


def generate_answer(state):
    emit_stream_event("node_start", name="Generate Answer")
    query = state["query"]
    docs = state.get("retrieved_docs", [])
    graph = state.get("graph_context", [])

    prompt = f"""
    You are a legal intelligence assistant. Answer the query using the provided context.
    If dependency or conflict graphs are provided, explain the multi-hop relationship clearly.

    Vector Context:
    {docs}

    Graph/Dependency Context:
    {graph}

    Query: {query}
    """
    response = qwen_llm.invoke(prompt)
    thinking, answer = _split_thinking(response.content)
    emit_stream_event("node_end", name="Generate Answer")
    return {
        "messages": [AIMessage(content=response.content)],
        "thinking": thinking,
        "answer": answer,
    }

