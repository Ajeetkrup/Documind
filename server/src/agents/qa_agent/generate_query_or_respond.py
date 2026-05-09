from langgraph.graph import MessagesState
from src.utils.llm import response_model
from src.agents.qa_agent.tools.retriever_tool import retriever_tool
from src.utils.stream_events import emit_stream_event

def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    emit_stream_event("node_start", name="generate_query_or_respond")
    response = (
        response_model
        .bind_tools([retriever_tool]).invoke(state["messages"])
    )
    emit_stream_event("node_end", name="generate_query_or_respond")
    return {"messages": [response]}