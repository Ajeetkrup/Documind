from langchain_core.tools import tool
from src.utils.retriever import retriever

@tool
def retriever_tool(query: str) -> str:
    """Search and return information from the uploaded documents."""
    docs = retriever.query(query)
    return "\n\n".join([doc.page_content for doc in docs])