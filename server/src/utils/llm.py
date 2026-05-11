from langchain_groq import ChatGroq
from src.utils.config import settings

# General purpose / routing
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

# Qwen — used for tool calls, grading, and answer generation in the legal agent
qwen_llm = ChatGroq(model="qwen/qwen3-32b", temperature=0, api_key=settings.GROQ_API_KEY)

qwen_llm_streaming = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    streaming=True,
    api_key=settings.GROQ_API_KEY,
)

# Legacy response models (kept for backward compatibility)
response_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=settings.GROQ_API_KEY)

stream_response_model = ChatGroq(
    model="openai/gpt-oss-120b",
    streaming=True,
    temperature=0,
    api_key=settings.GROQ_API_KEY,
)

grader_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=settings.GROQ_API_KEY)