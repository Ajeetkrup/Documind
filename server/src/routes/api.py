from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
from src.utils.evaluator import Evaluator

router = APIRouter()

def delete():
    import shutil, os

    if os.path.exists("./chroma"):
        shutil.rmtree("./chroma")

    if os.path.exists("./documents.json"):
        os.remove("./documents.json")

@router.post("/chat")
async def chat(query: str, background_tasks: BackgroundTasks):
    from src.agents.qa_agent.orchestrator import graph

    response = graph.invoke({
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    })

    evaluator = Evaluator()

    background_tasks.add_task(
        evaluator.evaluate_AgentGoalAccuracy,
        query,
        response
    )

    return {"message": response['messages'][-1].content}


@router.get("/chat/stream")
async def chat_stream(query: str):
    from src.agents.qa_agent.orchestrator import graph

    def event_stream():
        for chunk in graph.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                    }
                ]
            },
            stream_mode="custom",
        ):
            if isinstance(chunk, dict) and chunk.get("event") == "token":
                payload = {"token": chunk.get("data", "")}
                if payload["token"]:
                    yield f"data: {json.dumps(payload)}\n\n"
            elif isinstance(chunk, dict) and chunk.get("event") == "done":
                yield "data: {\"done\": true}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/upload-document")
async def upload_document(document: UploadFile = File(...)):
    """Handle document upload requests."""
    delete()

    from src.utils.injestion import DocumentIngestor
    ingestor = DocumentIngestor()
    file_content = await document.read()
    ingestor.ingest(file_content, filename=document.filename)
    return {"message": "Document uploaded successfully."}