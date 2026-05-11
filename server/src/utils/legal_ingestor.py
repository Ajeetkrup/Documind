import os
import uuid
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from pydantic import BaseModel, Field

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from langchain_groq import ChatGroq
from langchain_community.vectorstores.utils import filter_complex_metadata

from src.utils.nvidia_embeddings import get_embeddings
from src.utils.graph_store import MemgraphStore
from src.utils.config import settings

class ExtractionOutput(BaseModel):
    references: List[str] = Field(default_factory=list, description="References to other documents, policies, or clauses")
    conflicts_with: List[str] = Field(default_factory=list, description="Explicit conflicts with other documents, policies, or clauses")
    supersedes: List[str] = Field(default_factory=list, description="Documents, policies, or clauses that this supersedes")

class LegalIngestor:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.qdrant_url = settings.QDRANT_URL
        self.collection_name = "legal_docs"
        self.graph_store = MemgraphStore()
        
        # Initialize Groq for extraction
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0).with_structured_output(ExtractionOutput)
        
        # Docling setup
        # It's recommended to use a tokenizer that matches the embedding model.
        _hf_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.hf_tokenizer = HuggingFaceTokenizer(tokenizer=_hf_tokenizer)
        self.chunker = HybridChunker(tokenizer=self.hf_tokenizer)

    def ingest(self, file_content: bytes, filename: str = "document") -> None:
        ext = os.path.splitext(filename)[1]
        with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            loader = DoclingLoader(
                file_path=[tmp_path],
                export_type=ExportType.DOC_CHUNKS,
                chunker=self.chunker,
            )
            docs = loader.load()
            docs = filter_complex_metadata(docs)
            
            # For each chunk, extract relationships and store in Memgraph
            for doc in docs:
                chunk_id = str(uuid.uuid4())
                doc.metadata["chunk_id"] = chunk_id
                
                prompt = f"""
                Given the following legal clause, identify any references to other documents, policies, or clauses.
                Also identify if it explicitly conflicts with or supersedes anything.
                Clause: {doc.page_content}
                """
                try:
                    extraction = self.llm.invoke(prompt)
                    
                    self.graph_store.insert_clause_and_relationships(
                        chunk_id=chunk_id,
                        text=doc.page_content,
                        metadata=doc.metadata,
                        references=extraction.references,
                        conflicts_with=extraction.conflicts_with,
                        supersedes=extraction.supersedes
                    )
                except Exception as e:
                    print(f"Error extracting from chunk: {e}")
                    self.graph_store.insert_clause_and_relationships(
                        chunk_id=chunk_id,
                        text=doc.page_content,
                        metadata=doc.metadata,
                        references=[],
                        conflicts_with=[],
                        supersedes=[]
                    )

            # Store in Qdrant
            QdrantVectorStore.from_documents(
                documents=docs,
                embedding=self.embeddings,
                url=self.qdrant_url,
                collection_name=self.collection_name,
            )

            # Persist chunks locally for BM25 retrieval
            docs_dir = Path("docs")
            docs_dir.mkdir(exist_ok=True)
            bm25_path = docs_dir / "legal_docs.json"

            existing: list[dict] = []
            if bm25_path.exists():
                with open(bm25_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)

            existing.extend(
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in docs
            )

            with open(bm25_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
