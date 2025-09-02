# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/")
# async def test_classification():
#     return {"message": "Classification router working"}

from fastapi import APIRouter, Body
from services.classification_service import classify_document

router = APIRouter(prefix="/classification", tags=["Classification"])

@router.post("/")
async def classify_endpoint(text: str = Body(..., embed=True)):
    """
    Endpoint to classify a given document text.
    """
    result = await classify_document(text)
    return {"status": "success", "classification": result}
