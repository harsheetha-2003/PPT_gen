# # app/services/context_service.py
# from typing import Dict, Any, Optional
# from app.utils import render_template
# from app.services.llm_service import send_prompt_and_get_json

# TEMPLATE_FILE = "context_prompt.txt"

# def enrich_context(
#     document_text: str,
#     tone: str = "Formal",
#     style: str = "Corporate",
#     audience: str = "General Public",
#     layout: str = "Mixed",
#     template_name: str = "Professional",
#     additional_instructions: str = ""
# ) -> Dict[str, Any]:
#     """
#     Generate improved/organized content + suggested slide segmentation based on document.
#     Returns parsed JSON from LLM.
#     """
#     ctx = {
#         "document_content": document_text,
#         "tone": tone,
#         "style": style,
#         "audience": audience,
#         "layout": layout,
#         "template": template_name,
#         "additional_instructions": additional_instructions
#     }
#     system = "You are an assistant that reorganizes raw documents into slide-ready content. Return strict JSON."
#     user = render_template(TEMPLATE_FILE, **ctx)
#     parsed, notes = send_prompt_and_get_json(system, user)
#     if parsed is None:
#         return {"error": "LLM failed to enrich context", "notes": notes}
#     return parsed

# context_service.py
from utils import call_primary_llm, call_fallback_llm

def analyze_context(document_text: str) -> dict:
    """
    Analyzes context of the document text.
    Uses primary LLaMA and fallback Gemini for safety.
    """
    prompt = f"Analyze the following document for context and meaning:\n\n{document_text}"
    
    try:
        result = call_primary_llm(prompt)
    except Exception:
        result = call_fallback_llm(prompt)

    return {"context": result}
