# backend/app/services/routing_service.py
from app.utils import render_template
from app.services.llm_service import send_prompt_and_get_json if False else None

def decide_flow(prompt: str, document_present: bool, ppt_present: bool, additional_instructions: str=""):
    # For now, simple deterministic routing — could call LLM template if desired
    if ppt_present:
        return {"flow":"enhance_ppt","reason":"ppt provided"}
    if document_present:
        return {"flow":"prompt_plus_document","reason":"document provided"}
    if "research" in prompt.lower() or "data" in prompt.lower():
        return {"flow":"prompt_plus_document","reason":"topic suggests enrichment"}
    return {"flow":"prompt_only","reason":"default"}
