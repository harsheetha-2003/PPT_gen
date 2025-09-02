from fastapi import APIRouter, Body
from services.summarization_service import summarize_text

router = APIRouter(prefix="/summarization", tags=["Summarization"])

@router.post("/")
async def summarization_endpoint(text: str = Body(..., embed=True)):
    """
    Endpoint to summarize text.
    """
    result = await summarize_text(text)
    return {"status": "success", "summary": result}
