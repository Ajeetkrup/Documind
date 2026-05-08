from langchain_groq import ChatGroq
from src.utils.config import settings

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

response_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=settings.GROQ_API_KEY)

stream_response_model = ChatGroq(
    model="openai/gpt-oss-120b",
    streaming=True,
    temperature=0,
    api_key=settings.GROQ_API_KEY,
)

grader_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=settings.GROQ_API_KEY)