# backend/app/routers/llm.py
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import llm_service

router = APIRouter()

class GeneratePPTRequest(BaseModel):
    slides: int = 5
    template: str = "Professional"
    layout: str = "Mixed"
    images: bool = True
    image_level: str = "medium"
    tone: str = "Formal"
    style: str = "Corporate"
    audience: str = "General Public"
    topic: str
    additional_instructions: Optional[str] = ""
    web_search: bool = False
    web_depth: Optional[int] = None
    youtube_links: Optional[List[str]] = []
    youtube_depth: Optional[int] = None
    document_content: Optional[str] = None  # extracted text or empty
    temperature: float = 0.1
    max_tokens: int = 1024
    output_format: str = "pptx"  # or pdf

class GeneratePPTResponse(BaseModel):
    file_path: str
    llm_notes: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate_ppt", response_model=GeneratePPTResponse)
def generate_ppt(req: GeneratePPTRequest = Body(...)):
    try:
        result = llm_service.generate_presentation_from_request(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
