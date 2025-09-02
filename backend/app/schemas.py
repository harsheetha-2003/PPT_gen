from pydantic import BaseModel
from typing import Optional

# Common fields used in all flows
class PPTBaseRequest(BaseModel):
    slides: int
    template: str
    layout: str
    images: bool
    image_level: str  # "low", "medium", "high"
    tone: str
    style: str
    audience: str
    topic: str
    additional_instructions: Optional[str] = ""

# 1. Prompt-only
class PromptPPTRequest(PPTBaseRequest):
    pass

# 2. Document + prompt
class DocumentPPTRequest(PPTBaseRequest):
    document_content: str  # Extracted text from uploaded doc

# 3. Enhance PPT
class EnhancePPTRequest(PPTBaseRequest):
    ppt_content: str   # Extracted slide text
    slide_number: Optional[int] = None  # If None → apply to all
