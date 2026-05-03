from langchain_chroma import Chroma
from src.utils.onnx_embeddings import ONNXEmbeddings
import json
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

class HybridRetriever:
    def __init__(self):
        self.embedding = ONNXEmbeddings(model_path="onnx_output")
        self.vectorstore = Chroma(
            embedding_function=self.embedding,
            collection_name="docs",
            persist_directory="./chroma_db",
        )

        self.vector_retriever  = self.vectorstore.as_retriever(search_kwargs={"k": 4})

        with open("documents.json", "r") as f:
            raw_docs = json.load(f)

        documents = [
            Document(page_content=d["content"], metadata=d["metadata"])
            for d in raw_docs
        ]

        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = 4

        self.retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.vector_retriever],
            weights=[0.3, 0.7],
        )
    
    def query(self, question: str):
        return self.retriever.invoke(question)

retriever = HybridRetriever()