# backend/app/services/summarization_service.py
from app.utils import sumy_summarize
def summarize_text_for_pipeline(text: str, extract_sentences: int = 3, use_sumy_first: bool = True):
    # returns short extractive summary (SUMY) — LLM will later rewrite
    return sumy_summarize(text, sentences_count=extract_sentences)
