import json
from langchain_core.tools import tool
from src.utils.legal_retriever import legal_retriever
from src.utils.graph_store import MemgraphStore
from src.utils.stream_events import emit_stream_event


@tool
def contract_intelligence_retriever(query: str, strategy: str = "both") -> str:
    """
    Retrieves legal contract information.
    Use this tool to search for clauses, dependencies, conflicts, or superseding documents.
    Args:
        query: The search term or question to find in the documents.
        strategy: 'semantic' for general facts, 'graph' for conflicts/dependencies, or 'both'. Defaults to 'both'.
    """
    emit_stream_event("tool_start", name="Retriever Tool")
    retrieved_docs = []
    graph_context = []

    if strategy in ["semantic", "both"]:
        try:
            if legal_retriever.collection_exists():
                results = legal_retriever.query(query)
                retrieved_docs = [doc.page_content for doc in results]
        except Exception as e:
            print(f"Hybrid retrieval error: {e}")

    if strategy in ["graph", "both"]:
        try:
            store = MemgraphStore()
            cypher_query = """
            MATCH (c:Clause)-[r:REFERENCES|CONFLICTS_WITH|SUPERSEDES*1..2]-(target)
            WHERE toLower(c.text) CONTAINS toLower($search_term)
            RETURN c.text AS source, type(r) AS rel_type, target.name AS target_name, target.text AS target_text
            LIMIT 10
            """
            graph_context = store.execute_query(cypher_query, {"search_term": query})
            store.close()
        except Exception as e:
            print(f"Memgraph error: {e}")

    emit_stream_event("tool_end", name="Retriever Tool")
    return json.dumps({"vector_results": retrieved_docs, "graph_results": graph_context})
