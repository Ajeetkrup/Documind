from langchain_core.messages import HumanMessage
from src.utils.llm import response_model
from langgraph.graph import MessagesState
from src.utils.stream_events import emit_stream_event

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)


def rewrite_question(state: MessagesState):
    """Rewrite the original user question."""
    emit_stream_event("node_start", name="rewrite_question")
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    emit_stream_event("node_end", name="rewrite_question")
    return {"messages": [HumanMessage(content=response.content)]}