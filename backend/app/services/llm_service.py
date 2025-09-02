# backend/app/services/llm_service.py
import json, os
from typing import List, Optional
import requests
from app import config
from app.utils import (
    render_template, sumy_summarize, regulated_ddg_search,
    fetch_and_summarize_youtube, coerce_json
)
from app.services import ppt_service, image_service
from datetime import datetime

OPENROUTER_URL = config.OPENROUTER_API_URL
OPENROUTER_KEY = config.OPENROUTER_API_KEY
GEMINI_MODEL = config.OPENROUTER_GEMINI_MODEL
CLAUDE_MODEL = config.OPENROUTER_CLAUDE_MODEL

HEADERS = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}


def call_openrouter(model: str, system: str, user: str, max_tokens: int, temperature: float):
    payload = {
        "model": model,
        "messages": [{"role":"system","content":system},{"role":"user","content":user}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    r = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def ensure_slide_count(slides_list: List[dict], requested: int):
    slides = slides_list.copy()
    if len(slides) > requested:
        return slides[:requested]
    for i in range(len(slides), requested):
        slides.append({"slide_number": i+1, "title": f"Slide {i+1}", "content": ["(Add content)"], "speaker_notes": ""})
    for idx, s in enumerate(slides):
        s.setdefault("slide_number", idx+1)
        s.setdefault("title", f"Slide {s['slide_number']}")
        s.setdefault("content", [""])
        s.setdefault("speaker_notes", "")
    return slides


from app.services.export_service import save_and_record_export


def generate_presentation_from_request(req):
    """
    Main function to generate a presentation based on request object.
    Handles YouTube, web search, document content, LLM call, image generation, and PPT export.
    """

    # --- Depth settings ---
    web_depth = getattr(req, "web_depth", config.WEB_DEFAULT_DEPTH)
    youtube_depth = getattr(req, "youtube_depth", config.YOUTUBE_DEFAULT_DEPTH)

    # --- 1. Web / DuckDuckGo content ---
    ddg_text = ""
    if getattr(req, "web_search", False):
        topic_input = req.topic or getattr(req, "additional_instructions", None) or getattr(req, "prompt", None)
        ddg_text = regulated_ddg_search(topic_input, depth=web_depth)

    # --- 2. YouTube summaries ---
    yt_text = ""
    if getattr(req, "youtube_links", None):
        links = req.youtube_links if isinstance(req.youtube_links, list) else [req.youtube_links]
        # fetch_and_summarize_youtube now uses sentence_count to match sumy_summarize
        yt_text = fetch_and_summarize_youtube(links, depth=youtube_depth, sentence_count=2)

    # --- 3. Document content ---
    doc_text = getattr(req, "document_content", "")

    # --- 4. First-pass summarization using SUMY ---
    summarized_doc = sumy_summarize(doc_text, sentence_count=3) if doc_text else ""
    summarized_ddg = sumy_summarize(ddg_text, sentence_count=2) if ddg_text else ""
    summarized_yt = sumy_summarize(yt_text, sentence_count=2) if yt_text else ""

    # --- 5. Prepare template context for LLM ---
    template_ctx = {
        "topic": req.topic,
        "slides": req.slides,
        "template": req.template,
        "layout": req.layout,
        "images": str(getattr(req, "images", None)),
        "image_level": getattr(req, "image_level", None),
        "tone": getattr(req, "tone", None),
        "style": getattr(req, "style", None),
        "audience": getattr(req, "audience", None),
        "additional_instructions": getattr(req, "additional_instructions", None),
        "web_search": "Yes" if getattr(req, "web_search", False) else "No",
        "web_depth": web_depth,
        "youtube_summary": summarized_yt,
        "document_summary": summarized_doc,
        "ddg_summary": summarized_ddg
    }

    system_prompt = "You are an expert presentation creator. Output valid JSON only."
    user_prompt = render_template("ppt_generation.txt", **template_ctx)

    # --- 6. Call LLM (Gemini primary, Claude fallback) ---
    parsed = None
    notes = []
    for model in [GEMINI_MODEL, CLAUDE_MODEL]:
        try:
            resp = call_openrouter(
                model=model,
                system=system_prompt,
                user=user_prompt,
                max_tokens=getattr(req, "max_tokens", 500),
                temperature=getattr(req, "temperature", 0.7)
            )
            try:
                content = resp.get("choices", [])[0].get("message", {}).get("content", "").strip()
            except Exception:
                content = resp.get("choices", [])[0].get("text", "").strip()
            parsed = coerce_json(content)
            notes.append(f"Model {model} succeeded")
            break
        except Exception as e:
            notes.append(f"Model {model} error: {str(e)}")
            parsed = None
            continue

    if parsed is None:
        return {"file_path": "", "llm_notes": "\n".join(notes), "error": "LLM failed both primary and fallback"}

    slides = parsed.get("slides", [])
    if not isinstance(slides, list):
        slides = parsed.get("items", []) if isinstance(parsed.get("items", []), list) else []

    # --- 7. Normalize slides count ---
    slides = ensure_slide_count(slides, getattr(req, "slides", len(slides)))

    # --- 8. Generate images if requested ---
    if getattr(req, "images", False):
        for s in slides:
            img_prompt = s.get("image_prompt")
            if not img_prompt:
                img_prompt = render_template(
                    "ppt_image_prompt.txt",
                    style=getattr(req, "style", ""),
                    layout=getattr(req, "layout", ""),
                    audience=getattr(req, "audience", ""),
                    topic=req.topic,
                    image_level=getattr(req, "image_level", "")
                )
            if img_prompt:
                try:
                    img_paths = image_service.generate_images_for_prompt(img_prompt, n=1, size="1024x512")
                    if img_paths:
                        s["_image_path"] = img_paths[0]
                except Exception as e:
                    s["_image_error"] = str(e)

    # --- 9. Create PPT ---
    slides_obj = {"slides": slides}
    generated_ppt_path = ppt_service.create_presentation(
        slides_json=slides_obj,
        template=req.template,
        num_slides=getattr(req, "slides", len(slides)),
        output_format=getattr(req, "output_format", "pptx")
    )

    # --- 10. Save export record ---
    record = save_and_record_export(
        file_path=generated_ppt_path,
        topic=req.topic,
        audience=getattr(req, "audience", None),
        output_format=getattr(req, "output_format", "pptx")
    )

    return {
        "download_url": record.get("download_url"),
        "file_path": generated_ppt_path,
        "llm_notes": "\n".join(notes),
        "error": None
    }
