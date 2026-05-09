<div align="center">
  <h1>Documind</h1>
  <p><strong>Production-minded, agentic RAG system with transparent execution and reliable answers over private documents.</strong></p>
</div>

## Live Demo

[https://documind-production-81f2.up.railway.app/](https://documind-production-81f2.up.railway.app/)

## What This Project Demonstrates

Documind is a full-stack AI product that ingests enterprise-style documents and answers questions using an adaptive retrieval workflow. It is built to demonstrate practical engineering depth, not just a chatbot demo.

For recruiters and startup founders, this repo demonstrates:

- end-to-end product ownership (UI, API, retrieval pipeline, and deployment ergonomics),
- agentic RAG architecture with self-correction loops,
- execution transparency (node/tool lifecycle timeline in UI),
- security-aware prompting (prompt injection guardrails),
- measurable quality loops (RAGAS evaluation),
- production-grade observability (Arize Phoenix + OpenTelemetry),
- real-world platform decisions under constraints (Windows compatibility, local embeddings, vector DB trade-offs).

---

## Architecture Diagram

![Documind Architecture](docs/agent_architecture.png)

### High-Level Flow

1. User uploads a document (`/api/upload-document`).
2. Backend parses/chunks with Docling + HybridChunker.
3. Chunks are embedded with local ONNX embeddings and stored in Chroma.
4. User asks a question (`/api/chat` or `/api/chat/stream`).
5. LangGraph orchestrator routes through retrieve -> grade -> rewrite (if needed) -> answer.
6. Frontend receives ordered node/tool status events and renders execution timeline.
7. Final answer is streamed token-by-token during answer generation.
8. RAGAS evaluation runs in background for quality tracking.
9. Phoenix traces the pipeline for observability.

---

## Core Features (Implemented)

### 1) Agentic, Self-Correcting RAG Workflow

The QA pipeline is not a single retrieve-and-generate call. It is a graph:

- `generate_query_or_respond`: model decides whether retrieval is needed,
- `retrieve`: tool call to a hybrid retriever,
- `grade_documents`: checks retrieval relevance,
- `rewrite_question`: rewrites weak queries and loops back,
- `generate_answer`: creates final grounded response.

This gives controlled adaptation when first-pass retrieval is weak.

### 2) Execution Transparency in UI

The frontend shows step-by-step execution so users can see what the agent is doing:

- node status events (`node_start` -> `node_end`),
- tool status events (`tool_start` -> `tool_end`),
- visual running/done markers in the chat timeline,
- streamed final answer text while the `generate_answer` node runs.

This creates trust and improves debuggability during real usage.

### 3) Prompt Injection Guardrails

Guardrails are explicitly embedded in prompts for both grading and answering:

- retrieved context is marked as **UNTRUSTED**,
- model is told to ignore instructions inside context,
- model is constrained to relevance-checking or factual extraction only.

This protects against malicious instructions buried in uploaded files.

### 4) Hybrid Retriever (Semantic + Keyword)

Retrieval combines:

- dense vector search via Chroma + ONNX embeddings,
- sparse keyword search via BM25,
- weighted ensemble (0.7 dense, 0.3 BM25).

Why it matters: semantic retrieval catches meaning; BM25 catches exact terms/entities. Ensemble retrieval is more robust than either alone.

### 5) Local ONNX Embeddings

Embeddings run from a local ONNX model for predictable inference and lower vendor lock-in at retrieval time.

### 6) RAGAS Quality Check

Each chat request schedules a background evaluation using:

- `AgentGoalAccuracyWithReference`,
- LangGraph-to-RAGAS message conversion,
- async scoring pipeline.

This creates a measurable feedback loop for answer quality.

### 7) Arize Phoenix Observability

The app is instrumented with Phoenix OpenTelemetry registration in backend startup:

- traces capture agent execution paths,
- helps debug routing/retrieval behavior,
- supports iteration with visibility instead of guesswork.

### 8) Full-Stack Product UX

Frontend includes:

- drag-and-drop file upload,
- ingestion state feedback,
- document-aware chat gating (forces upload before querying),
- execution timeline with per-node/per-tool status,
- final-answer streaming via SSE,
- markdown response rendering,
- responsive sidebar/chat experience.

---

## Why This Is Hard

Building a reliable RAG product is hard because you are solving multiple systems problems at once:

- **Retrieval quality is non-deterministic**: a single bad query can return weak context and collapse answer quality.
- **Documents are messy**: real PDFs contain structural metadata that many vector stores cannot ingest directly.
- **Security is subtle**: retrieved text can contain adversarial instructions that hijack generation.
- **Infra is platform-dependent**: Windows filesystem behavior and vector DB packaging constraints can break "standard" setups.
- **LLM apps need observability**: without traces and evals, failures feel random and are difficult to improve.

Documind addresses these with explicit architecture, not one-off patches.

---

## Key Engineering Decisions (And Why)

### Decision 1: LangGraph state machine over linear chains
- **Why:** Needed explicit control over branching, looping, and deterministic node transitions.
- **Impact:** Enables self-correction and explainable execution flow.

### Decision 2: Hybrid retriever over pure vector search
- **Why:** Dense retrieval misses exact keywords in some cases; BM25 misses semantic paraphrases.
- **Impact:** Better recall across varied query styles.

### Decision 3: ChromaDB over Milvus-lite for local Windows dev
- **Why:** Milvus-lite support is not Windows-friendly in this setup.
- **Impact:** Preserved local persistent vector storage without Docker dependency.

### Decision 4: Filter complex metadata before indexing
- **Why:** Docling outputs nested metadata that Chroma rejects.
- **Impact:** Prevented ingestion failures while retaining useful searchable content.

### Decision 5: Explicit execution event contract for frontend
- **Why:** Users and developers need deterministic, ordered visibility into graph progress.
- **Impact:** Stable SSE schema (`run_id`, `seq`, `type`, `name`, `payload`) powers timeline UI and easier debugging.

### Decision 6: Stream only final-answer tokens
- **Why:** Streaming every intermediate token creates noisy UX and weak signal-to-noise.
- **Impact:** Cleaner experience: status timeline for process, live tokens for final answer only.

### Decision 7: Explicit anti-injection prompt constraints
- **Why:** Retrieved context is untrusted and can contain malicious prompt instructions.
- **Impact:** Improves safety posture during grading and answering.

### Decision 8: Background RAGAS evaluation
- **Why:** Quality must be measured continuously without blocking user latency.
- **Impact:** Practical signal for iterative improvement.

### Decision 9: Phoenix OTEL instrumentation
- **Why:** Agentic systems need trace-level visibility to debug routing and retrieval behavior.
- **Impact:** Faster diagnosis and safer production iteration.

---

## Tech Stack

- **Frontend:** React 19, Vite, Lucide, React Markdown
- **Backend:** FastAPI, Python
- **Agent Orchestration:** LangGraph, LangChain
- **LLM Serving:** Groq-hosted models (for response + grading)
- **Embeddings:** Local ONNX Runtime + Transformers tokenizer
- **Document Parsing/Chunking:** Docling + HybridChunker
- **Retrieval:** Chroma vector search + BM25 + EnsembleRetriever
- **Evaluation:** RAGAS
- **Observability:** Arize Phoenix + OpenTelemetry
- **Containerization:** Docker (backend image + runtime)

---

## Repository Structure

```text
Documind/
├─ docs/
│  └─ agent_architecture.png
├─ frontend/
│  └─ src/
│     ├─ App.jsx
│     └─ components/
└─ server/
   ├─ requirements.txt
   └─ src/
      ├─ main.py
      ├─ routes/api.py
      ├─ agents/qa_agent/
      └─ utils/
```

---

## API Surface

- `POST /api/upload-document`  
  multipart upload; ingests and indexes a single document.

- `POST /api/chat?query=...`  
  runs agentic retrieval workflow and returns full model response after completion.

- `GET /api/chat/stream?query=...`  
  streams execution and answer events as Server-Sent Events (SSE).
  Event payload structure:
  - `type`: event kind (`run_start`, `node_start`, `tool_start`, `answer_token`, `run_end`, etc.)
  - `run_id`: unique run identifier
  - `seq`: monotonic event sequence number
  - `ts`: UTC timestamp
  - `name` (optional): node/tool name
  - `payload` (optional): event data (`token`, decision info, final answer)

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for containerized backend run)

### 1) Backend

```bash
cd server
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create `server/.env` with:

```env
NVIDIA_API_KEY=your_key
GROQ_API_KEY=your_key
PHOENIX_API_KEY=your_key
PHOENIX_COLLECTOR_ENDPOINT=your_phoenix_endpoint
```

Run backend:

```bash
uvicorn src.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Create `frontend/.env` (if not already present):

```env
VITE_API_BASE_URL=http://localhost:8000
```

The frontend uses `GET /api/chat/stream` for execution timeline + final-answer streaming and keeps `POST /api/chat` as a non-stream fallback.

---

## Docker Run (Backend)

Build image from repo root:

```bash
docker build -t documind-server -f server/Dockerfile server
```

Run container:

```bash
docker run --name documind-server \
  --env-file server/.env \
  -p 8004:80 \
  documind-server
```

Then set frontend API base URL:

```env
VITE_API_BASE_URL=http://localhost:8004
```

---

## Troubleshooting and Operational Notes

Known platform and ingestion issues are documented in `TROUBLESHOOTING.md`, including:

- tokenizer max token context mismatch,
- Hugging Face symlink privilege issues on Windows,
- Milvus-lite compatibility constraints,
- Chroma metadata schema limits.

---

## What a CTO Can Assess from This Repo

- Can this engineer design beyond happy-path demos? **Yes**: graph orchestration, fallback loops, eval, tracing, structured execution events.
- Can they make trade-offs under platform constraints? **Yes**: Windows symlink fallback and vector DB migration.
- Do they think about reliability and safety? **Yes**: guardrails, relevance grading, ordered streaming contract, background quality checks.
- Can they ship product-facing UX with technical depth? **Yes**: complete upload-to-answer user flow with transparent runtime status.

---

## Next Improvements

- multi-document corpus management instead of reset-on-upload
- citations and source spans in answer rendering
- auth + tenant isolation
- automated regression datasets for eval baselines
- docker-compose profile for one-command full-stack local launch
