# from fastapi import APIRouter

# router = APIRouter()

# @router.post("/analyze")
# async def analyze_context(data: dict):
#     text = data.get("text", "")
#     return {"original_text": text, "context_summary": f"Processed: {text[:30]}..."}

from fastapi import APIRouter, Body
from services.context_service import analyze_context

router = APIRouter(prefix="/context", tags=["Context"])

@router.post("/")
async def context_endpoint(text: str = Body(..., embed=True)):
    """
    Endpoint to analyze context from text.
    """
    result = await analyze_context(text)
    return {"status": "success", "context": result}
