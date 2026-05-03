# Documind Troubleshooting & Error Resolution Guide

This document catalogs the major errors encountered while building the document ingestion and retrieval pipeline (RAG), explaining *why* they happened and exactly *how* they were resolved.

---

## 1. Docling Tokenizer Context Window Error
**Error:** `RuntimeError: max_tokens could not be determined automatically; please set explicitly.`  
**Location:** `src/utils/injestion.py`

**Root Cause:**
Docling uses the HuggingFace tokenizer to securely chunk documents so they don't exceed your embedding model's context window. Because you were loading custom local ONNX embeddings (`onnx_output`), the configuration file did not contain a valid `model_max_length` attribute. Instead of guessing, Docling intentionally throws an error to prevent crashing your embedding model later.

**Resolution:**
Explicitly passed `max_tokens=512` to the tokenizer initialization, as 512 is the standard maximum context window for almost all local text embedding models.
```python
self.hf_tokenizer = HuggingFaceTokenizer(tokenizer=self.embedding.tokenizer, max_tokens=512)
```

---

## 2. HuggingFace Model Download Crash on Windows (WinError 1314)
**Error:** `OSError: [WinError 1314] A required privilege is not held by the client.`  
**Location:** Anywhere `docling` or `transformers` attempts to download a model.

**Root Cause:**
When downloading heavy models (like Docling's Layout model), the `huggingface_hub` package attempts to use **symbolic links** to cache the files efficiently. However, Windows strictly prohibits standard (non-administrator) users from creating symbolic links unless "Developer Mode" is enabled.

**Resolution:**
Created a "monkeypatch" at the very top of `src/main.py`. This intercepts any request `huggingface_hub` makes to `os.symlink` and physically copies the file using `shutil.copy2()` instead. (Note: The patch required converting relative paths to absolute paths to prevent silent file-not-found errors).

---

## 3. Milvus-Lite Failing on Windows
**Error:** `ModuleNotFoundError: No module named 'milvus_lite'`  
**Location:** Connecting to `./milvus.db` in `injestion.py`.

**Root Cause:**
`langchain-milvus` attempts to use the `milvus-lite` package to create a seamless local database file (`.db`). However, **Milvus-lite does not natively support Windows**. It is strictly compiled for Linux and macOS environments. 

**Resolution:**
To achieve the exact same functionality (a persistent, local vector database running directly on your Windows machine without Docker), the entire vector store implementation was swapped from Milvus to **ChromaDB** (`langchain-chroma`).

---

## 4. LangChain Milvus ORM Connection Quirks
**Error:** `ConnectionNotExistException: (code=1, message=should create connection first.)`  
**Location:** Connecting to a local Milvus Docker container (`http://localhost:19530`).

**Root Cause:**
When attempting to bypass the `milvus-lite` issue by spinning up a Docker container, LangChain's `Milvus` initialization failed. This is a known bug/quirk in LangChain: while it creates a new `MilvusClient`, it still relies on the legacy `pymilvus` Object Relational Mapper (ORM) system for caching. If the connection isn't explicitly registered in the global ORM registry first, the legacy system crashes.

**Resolution:**
Explicitly registered the global connection before initializing the vector store:
```python
from pymilvus import connections
connections.connect(alias="default", uri="http://localhost:19530")
```

---

## 5. ChromaDB Rejecting Docling Metadata
**Error:** `ValueError: Expected metadata value to be a str, int, float, bool... got {'schema_name': ... 'doc_items': [...]}`  
**Location:** `Chroma.from_documents()` in `injestion.py`.

**Root Cause:**
`DoclingLoader` extracts incredibly rich metadata (like physical bounding box coordinates, paragraph hierarchy trees, and page provenance). It stores these as deeply nested JSON lists and dictionaries. However, ChromaDB strictly requires "flat" metadata (only simple strings, numbers, or booleans).

**Resolution:**
Applied LangChain's built-in metadata filter right before insertion to safely strip out the nested JSON structures while preserving the actual chunk text and standard flat metadata (like source filenames).
```python
from langchain_community.vectorstores.utils import filter_complex_metadata

docs = loader.load()
docs = filter_complex_metadata(docs)
Chroma.from_documents(documents=docs, ...)
```