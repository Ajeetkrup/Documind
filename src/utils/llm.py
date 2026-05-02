from langchain_nvidia_ai_endpoints import ChatNVIDIA
from src.utils.config import settings

response_model = ChatNVIDIA(model="z-ai/glm4.7", temperature=0, api_key=settings.NVIDIA_API_KEY)

grader_model =  ChatNVIDIA(model="z-ai/glm4.7", temperature=0, api_key=settings.NVIDIA_API_KEY)