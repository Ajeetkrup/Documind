from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/chat")
def chat(query: str):
    """Handle chat requests."""
    from src.agents.qa_agent.orchestrator import graph
    response = graph.invoke({
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    })
    return response

@router.post("/upload-document")
async def upload_document(document: UploadFile = File(...)):
    """Handle document upload requests."""
    from src.utils.injestion import DocumentIngestor
    ingestor = DocumentIngestor()
    file_content = await document.read()
    ingestor.ingest(file_content, filename=document.filename)
    return {"message": "Document uploaded successfully."}