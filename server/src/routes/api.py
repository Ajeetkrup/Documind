from fastapi import APIRouter, File, UploadFile, BackgroundTasks
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

@router.post("/upload-document")
async def upload_document(document: UploadFile = File(...)):
    """Handle document upload requests."""
    delete()

    from src.utils.injestion import DocumentIngestor
    ingestor = DocumentIngestor()
    file_content = await document.read()
    ingestor.ingest(file_content, filename=document.filename)
    return {"message": "Document uploaded successfully."}