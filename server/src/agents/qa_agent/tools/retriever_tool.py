from langchain_core.tools import tool
from src.utils.retriever import retriever
from src.utils.stream_events import emit_stream_event

@tool
def retriever_tool(query: str) -> str:
    """Search and return information from the uploaded documents."""
    emit_stream_event("tool_start", name="retriever_tool")
    docs = []
    try:
        docs = retriever.query(query)
        return "\n\n".join([doc.page_content for doc in docs])
    finally:
        emit_stream_event(
            "tool_end",
            name="retriever_tool",
            payload={"document_count": len(docs)},
        )