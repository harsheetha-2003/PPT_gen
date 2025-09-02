from fastapi import APIRouter, Body
from services.ppt_service import generate_ppt

router = APIRouter(prefix="/ppt", tags=["PPT"])

@router.post("/")
async def ppt_endpoint(content: str = Body(..., embed=True), title: str = Body("Generated PPT", embed=True)):
    """
    Endpoint to generate PPT from content.
    """
    file_path = await generate_ppt(content, title)
    return {"status": "success", "file_path": file_path}
