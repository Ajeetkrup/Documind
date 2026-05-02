from langchain_chroma import Chroma
from src.utils.onnx_embeddings import ONNXEmbeddings

embedding = ONNXEmbeddings(model_path="onnx_output")

vectorstore = Chroma(
    embedding_function=embedding,
    collection_name="docs",
    persist_directory="./chroma_db",
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})