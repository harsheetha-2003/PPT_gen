# # backend/app/services/classification_service.py
# from app.utils import render_template
# from app.services.llm_service import send_prompt_and_get_json if False else None
# # Minimal local classifier: decide whether to use doc/web/youtube or prompt-only
# def basic_classify(prompt: str, document_present: bool, ppt_present: bool, youtube_links, web_search_flag):
#     # Heuristic
#     if ppt_present:
#         return {"flow":"enhance_ppt","reason":"ppt uploaded"}
#     if document_present:
#         return {"flow":"prompt_plus_document","reason":"document uploaded"}
#     if web_search_flag or (youtube_links and len(youtube_links)>0):
#         return {"flow":"prompt_plus_document","reason":"web or youtube enrichment requested"}
#     return {"flow":"prompt_only","reason":"simple prompt"}

# classification_service.py
from utils import call_primary_llm, call_fallback_llm

def classify_document(document_text: str) -> dict:
    """
    Classifies the given document into categories.
    Uses LLaMA 3.1 (primary) and Gemini Flash 1.5 (fallback).
    """
    prompt = f"Classify the following document:\n\n{document_text}\n\nReturn categories."
    
    try:
        result = call_primary_llm(prompt)
    except Exception:
        result = call_fallback_llm(prompt)

    return {"classification": result}
