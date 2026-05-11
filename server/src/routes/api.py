from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse
import json
from datetime import datetime, timezone
import uuid
from src.utils.evaluator import Evaluator

router = APIRouter()

@router.post("/chat")
async def chat(query: str, background_tasks: BackgroundTasks):
    from src.agents.legal_agent.orchestrator import graph

    response = graph.invoke({
        "messages": [HumanMessage(content=query)]
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
    from src.agents.legal_agent.orchestrator import graph

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
                    "messages": [HumanMessage(content=query)]
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
            thinking = ""
            if latest_values:
                thinking = latest_values.get("thinking", "")
                answer = latest_values.get("answer", "")
                if answer:
                    final_answer = answer
                elif latest_values.get("messages"):
                    last_message = latest_values["messages"][-1]
                    final_answer = getattr(last_message, "content", str(last_message))

            yield serialize_event("run_end", payload={"answer": final_answer, "thinking": thinking})
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
    from src.utils.legal_ingestor import LegalIngestor
    ingestor = LegalIngestor()
    file_content = await document.read()
    ingestor.ingest(file_content, filename=document.filename)
    return {"message": "Document uploaded successfully."}