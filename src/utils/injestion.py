import os
from tempfile import NamedTemporaryFile
from langchain_milvus import Milvus
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from src.utils.onnx_embeddings import ONNXEmbeddings
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer


from langchain_chroma import Chroma

from langchain_community.vectorstores.utils import filter_complex_metadata

class DocumentIngestor:
    def __init__(self, model_path: str = "onnx_output", persist_directory: str = "./chroma_db"):
        self.embedding = ONNXEmbeddings(model_path=model_path)
        self.hf_tokenizer = HuggingFaceTokenizer(tokenizer=self.embedding.tokenizer, max_tokens=512)
        self.chunker = HybridChunker(tokenizer=self.hf_tokenizer)
        self.persist_directory = persist_directory

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

            Chroma.from_documents(
                documents=docs,
                embedding=self.embedding,
                collection_name="docs",
                persist_directory=self.persist_directory,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
