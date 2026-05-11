import json
from src.agents.legal_agent.state import GraphRAGState


def parse_tool_results(state: GraphRAGState):
    messages = state.get("messages", [])
    retrieved_docs = []
    graph_context = []

    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.__class__.__name__ == "ToolMessage":
            try:
                data = json.loads(msg.content)
                retrieved_docs = data.get("vector_results", [])
                graph_context = data.get("graph_results", [])
            except Exception:
                pass
            break

    return {"retrieved_docs": retrieved_docs, "graph_context": graph_context}
