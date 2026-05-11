from langchain_core.messages import HumanMessage
from src.agents.legal_agent.state import GraphRAGState
from src.agents.legal_agent.tools import contract_intelligence_retriever
from src.utils.llm import qwen_llm
from src.utils.stream_events import emit_stream_event


def retrieval_agent_node(state: GraphRAGState):
    """Calls Qwen with the retrieval tool bound so it decides when to invoke it."""
    emit_stream_event("node_start", name="Retrieval Agent")
    llm_with_tools = qwen_llm.bind_tools([contract_intelligence_retriever])

    query = state.get("query", "")
    strategy = state.get("strategy", "both")

    prompt = (
        f"Use the contract_intelligence_retriever tool with strategy='{strategy}' "
        f"to answer: {query}"
    )
    response = llm_with_tools.invoke([HumanMessage(content=prompt)])
    emit_stream_event("node_end", name="Retrieval Agent")
    return {"messages": [response]}
