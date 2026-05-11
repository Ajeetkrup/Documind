import json
from pathlib import Path
from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from src.utils.nvidia_embeddings import get_embeddings
from src.utils.config import settings

BM25_DOCS_PATH = Path("docs") / "legal_docs.json"


class LegalHybridRetriever:
    COLLECTION = "legal_docs"
    K = 5

    def __init__(self):
        self.embeddings = get_embeddings()
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self._ensemble: EnsembleRetriever | None = None

    def _load_bm25_documents(self) -> list[Document]:
        if not BM25_DOCS_PATH.exists():
            return []
        with open(BM25_DOCS_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [
            Document(page_content=d["content"], metadata=d.get("metadata", {}))
            for d in raw
            if d.get("content")
        ]

    def _build_ensemble(self) -> EnsembleRetriever:
        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.COLLECTION,
            embedding=self.embeddings,
        )
        vector_retriever = vector_store.as_retriever(search_kwargs={"k": self.K})

        documents = self._load_bm25_documents()
        if not documents:
            return EnsembleRetriever(
                retrievers=[vector_retriever],
                weights=[1.0],
            )

        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = self.K

        return EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.3, 0.7],
        )

    def query(self, question: str) -> list[Document]:
        if self._ensemble is None:
            self._ensemble = self._build_ensemble()
        return self._ensemble.invoke(question)

    def collection_exists(self) -> bool:
        return self.qdrant_client.collection_exists(self.COLLECTION)


legal_retriever = LegalHybridRetriever()
