<div align="center">
  <h1>Legal Intelligence</h1>
  <p><strong>Contract Risk & Dependency Intelligence System powered by Multi-hop Graph RAG and Agentic Workflows.</strong></p>
  
  <br />
  <img src="docs/Legal Intelligence – default.jpg" alt="Welcome Screen" width="48%">
  <img src="docs/Legal Intelligence – Query.jpg" alt="Query Execution Screen" width="48%">
</div>

## The Problem

Large enterprises manage thousands of contracts, vendor agreements, DPAs, compliance docs, internal policies, and regulations. Lawyers spend an immense amount of time:
- Finding dependencies across documents
- Tracing references and liability obligations
- Checking for conflicts in obligations
- Reviewing terms
- Validating compliance

This manual work is repetitive, expensive, and error-prone. 

## The Solution

**Legal Intelligence** automates due diligence, finds cross-contract dependencies, and resolves conflicting obligations instantly. By combining semantic vector search with knowledge graph traversals, this system mimics a lawyer's multi-hop reasoning process.

---

## Core Features

### 1) Multi-Hop Graph RAG (Dependency Tracing)
Legal Intelligence doesn't just do basic text matching. It uses **Memgraph** to trace relationships between clauses, definitions, and distinct contracts (e.g., finding how a DPA supersedes a master vendor agreement).

### 2) Semantic Context & Conflict Detection
Uses **Qdrant** alongside state-of-the-art **NVIDIA Embeddings** to semantically understand legal text and identify conflicting clauses or compliance violations across large corpora.

### 3) Agentic Routing & Self-Correction
Orchestrated via **LangGraph**:
- `router`: Intelligently decides if a query needs semantic search, graph traversal, both, or if it's a direct conversational query that requires no retrieval.
- `grade_documents`: Automatically scores retrieved legal context for relevance.
- `rewrite_query`: If retrieval fails to find relevant clauses, the agent rewrites the query and tries again.

### 4) Execution Transparency (UI)
The frontend features a "Mesmerizing" deep black and neon green UI that provides a live execution timeline. You can see exactly which nodes and tools are running, building trust in the system's reasoning process. The model's internal `<think>` reasoning blocks are also neatly separated from the final answer.

### 5) Advanced Document Parsing
Leverages **Docling** for deep structural parsing of complex PDFs and DOCX files, ensuring tables, lists, and hierarchical headings are properly indexed.

### 6) Production-Grade Observability & Evaluation
Integrated with **Arize Phoenix** for OpenTelemetry tracing of agent executions, and **Ragas** for measuring RAG quality (Context Precision, Answer Relevancy).

---

## Tech Stack

- **Frontend**: React 19, Vite, Lucide React, Custom Dark/Neon Green UI
- **Backend**: FastAPI, Python, Server-Sent Events (SSE) for streaming
- **Agent Orchestration**: LangGraph, LangChain
- **LLM Serving**: Groq (Llama 3 / Qwen) and NVIDIA NIM
- **Embeddings**: NVIDIA Embeddings (`nvidia-nim`)
- **Document Parsing**: Docling
- **Vector Database**: Qdrant (Semantic Search)
- **Graph Database**: Memgraph (Dependency & Entity relationships)
- **Observability**: Arize Phoenix, OpenTelemetry
- **Infrastructure**: Docker Compose

---

## Architecture Flow

1. **Ingestion (`/api/upload-document`)**: 
   - Document is parsed by Docling.
   - Text is chunked, embedded via NVIDIA, and stored in Qdrant.
   - Entities and relationships (dependencies, superseding clauses) are extracted and pushed to Memgraph.
2. **Querying (`/api/chat/stream`)**: 
   - User asks a complex contract question.
   - **Router** classifies the query (Semantic, Graph, Both, or Direct).
   - **Retrieval Agent** executes queries against Qdrant and/or Memgraph via tool calls.
   - Results are graded for relevance.
   - Final generation streams the reasoning (`<think>`) and answer back to the UI.

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (required for Qdrant, Memgraph, and containerized deployment)

### 1) Environment Variables

Create `server/.env`:
```env
NVIDIA_API_KEY=your_nvidia_key
GROQ_API_KEY=your_groq_key
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
```

### 2) Run Infrastructure (Databases + Backend + Frontend)

The easiest way to run the entire stack is using Docker Compose:

```bash
docker compose up --build -d
```

This will spin up:
- **Qdrant** (Vector DB)
- **Memgraph** (Graph DB)
- **Backend API** (FastAPI on port 8000)
- **Frontend UI** (Vite on port 5173)

Open `http://localhost:5173` to interact with Legal Intelligence.

---

## API Surface

- `POST /api/upload-document`  
  Ingests and indexes a single legal document (PDF, DOCX, TXT) into both Qdrant and Memgraph.

- `GET /api/chat/stream?query=...`  
  Streams execution steps, tool calls, model reasoning, and the final answer as Server-Sent Events (SSE).

---

## Key Engineering Decisions (And Why)

Building a reliable AI legal product is hard. You are solving multiple systems problems at once: non-deterministic retrieval, messy PDF structures, and security against prompt injection. Here is how Legal Intelligence addresses these challenges:

### Decision 1: Multi-Hop Graph RAG over Vector-Only RAG
- **Why:** Contracts are heavily cross-referenced. Vector search might find a "liability clause," but it won't easily find "which vendor agreement is superseded by this DPA."
- **Impact:** By combining **Qdrant** (semantic search) and **Memgraph** (relationship traversal), the system correctly answers complex dependency questions that standard RAG fails on.

### Decision 2: LangGraph State Machine over Linear Chains
- **Why:** Needed explicit control over branching, looping, and deterministic node transitions.
- **Impact:** Enables the agent to self-correct (e.g., rewriting weak queries) and intelligently route conversational vs. analytical queries, ensuring reliability.

### Decision 3: Explicit Execution Event Contract for Frontend
- **Why:** Users need deterministic, ordered visibility into graph progress to trust the system.
- **Impact:** A stable Server-Sent Events (SSE) schema powers the live timeline UI, allowing the user to watch the agent "think" and execute tools in real-time.

### Decision 4: Separation of Reasoning and Answer
- **Why:** Large models generate better answers when allowed to "think" out loud, but exposing raw reasoning mixed with the final answer creates a poor UX.
- **Impact:** The backend explicitly parses `<think>` blocks, streaming them to a collapsible "Reasoning" UI component, keeping the final output clean and authoritative.

### Decision 5: Background Evaluation & Observability
- **Why:** "Vibes" are not a valid testing strategy for legal tech.
- **Impact:** Every inference trace is sent to **Arize Phoenix** via OpenTelemetry. Retrieval context and generation relevance are evaluated using **Ragas** metrics, providing concrete signals for improvement.

---

## What a CTO or Recruiter Can Assess from This Repo

- **Can this engineer design beyond happy-path demos?** **Yes**: This project features graph orchestration, fallback loops, deterministic routing, and structured execution events.
- **Can they make complex architectural trade-offs?** **Yes**: Moving beyond simple vector DBs to a hybrid Vector + Graph architecture using Memgraph and Qdrant for accurate dependency tracing.
- **Do they think about reliability and user trust?** **Yes**: The mesmerizing UI isn't just for show; it exposes the agent's internal state machine transparently, building user confidence.
- **Can they ship product-facing UX with technical depth?** **Yes**: Complete end-to-end ownership—from complex backend data ingestion and agentic workflows to a highly polished, responsive frontend.

---

## Next Steps / Roadmap

- Multi-tenant data isolation for enterprise deployment.
- Exact citation highlighting directly within the original PDF viewer.
- Automated compliance checklists based on uploaded policies.
