from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.agents.legal_agent.state import GraphRAGState
from src.agents.legal_agent.router import route_query
from src.agents.legal_agent.retrieval_agent import retrieval_agent_node
from src.agents.legal_agent.parse_results import parse_tool_results
from src.agents.legal_agent.tools import contract_intelligence_retriever
from src.agents.legal_agent.grade_documents import grade_documents, check_relevance, rewrite_query
from src.agents.legal_agent.generate_answer import generate_answer

workflow = StateGraph(GraphRAGState)

workflow.add_node("router", route_query)
workflow.add_node("retrieval_agent", retrieval_agent_node)
workflow.add_node("retrieve", ToolNode([contract_intelligence_retriever]))
workflow.add_node("parse_results", parse_tool_results)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("generate_answer", generate_answer)

workflow.add_edge(START, "router")

def route_decision(state: GraphRAGState):
    if state.get("strategy") == "direct":
        return "generate_answer"
    return "retrieval_agent"

workflow.add_conditional_edges(
    "router",
    route_decision,
    {"generate_answer": "generate_answer", "retrieval_agent": "retrieval_agent"},
)
workflow.add_edge("retrieval_agent", "retrieve")
workflow.add_edge("retrieve", "parse_results")
workflow.add_edge("parse_results", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    check_relevance,
    {"generate": "generate_answer", "rewrite": "rewrite_query"},
)
workflow.add_edge("rewrite_query", "retrieval_agent")
workflow.add_edge("generate_answer", END)

graph = workflow.compile()
