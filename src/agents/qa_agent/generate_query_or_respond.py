from langgraph.graph import MessagesState
from src.utils.llm import response_model
from src.agents.qa_agent.tools.retriever_tool import retriever_tool

def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    response = (
        response_model
        .bind_tools([retriever_tool]).invoke(state["messages"])
    )
    return {"messages": [response]}