import os
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

def get_embeddings():
    return NVIDIAEmbeddings(
        model="nvidia/nv-embed-v1",
        truncate="END"
    )
