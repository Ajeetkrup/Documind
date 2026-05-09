from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
from datetime import datetime, timezone
import uuid
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
        run_id = str(uuid.uuid4())
        sequence = 0
        latest_values = None

        def serialize_event(event_type: str, name: str | None = None, payload: dict | None = None):
            nonlocal sequence
            sequence += 1
            event = {
                "type": event_type,
                "run_id": run_id,
                "seq": sequence,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if name:
                event["name"] = name
            if payload is not None:
                event["payload"] = payload
            return f"data: {json.dumps(event)}\n\n"

        yield serialize_event("run_start")
        try:
            for streamed in graph.stream(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": query,
                        }
                    ]
                },
                stream_mode=["values", "custom"],
            ):
                if isinstance(streamed, tuple) and len(streamed) == 2:
                    mode, chunk = streamed
                else:
                    mode, chunk = "custom", streamed

                if mode == "values":
                    latest_values = chunk
                    continue

                if mode != "custom" or not isinstance(chunk, dict):
                    continue

                event_type = chunk.get("type")
                if not event_type:
                    continue

                name = chunk.get("name")
                payload = chunk.get("payload")
                yield serialize_event(event_type, name=name, payload=payload)

            final_answer = ""
            if latest_values and latest_values.get("messages"):
                last_message = latest_values["messages"][-1]
                final_answer = getattr(last_message, "content", last_message)
                if not isinstance(final_answer, str):
                    final_answer = str(final_answer)

            yield serialize_event("run_end", payload={"answer": final_answer})
        except Exception as exc:
            yield serialize_event("error", payload={"message": str(exc)})

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