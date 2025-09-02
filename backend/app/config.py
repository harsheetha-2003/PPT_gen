# backend/app/config.py
import os
from dotenv import load_dotenv

# OpenRouter (Gemini 1.5 flash binding + Claude fallback)
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://api.openrouter.ai/v1/chat/completions")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Put the exact binding/model names OpenRouter gave for Gemini 1.5 flash and Claude
OPENROUTER_GEMINI_MODEL = os.getenv("OPENROUTER_GEMINI_MODEL", "gemini-1.5-flash")  
OPENROUTER_CLAUDE_MODEL = os.getenv("OPENROUTER_CLAUDE_MODEL", "claude-3.5")

# Stable Diffusion API
# STABLE_DIFFUSION_API_URL = os.getenv("STABLE_DIFFUSION_API_URL", "https://api.stablediffusionapi.com/v3/text2img")
# STABLE_DIFFUSION_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("STABLE_DIFFUSION_API_KEY", "")
OPENROUTER_API_URL = os.getenv(
    "STABLE_DIFFUSION_API_URL", "https://api.stablediffusionapi.com/v3/text2img"
)

# Local output folders
OUTPUT_PPT_DIR = os.getenv("OUTPUT_PPT_DIR", "generated_ppts")
OUTPUT_IMAGE_DIR = os.getenv("OUTPUT_IMAGE_DIR", "generated_images")

# Web/YT defaults
WEB_SEARCH_ALLOWED = os.getenv("WEB_SEARCH_ALLOWED", "true").lower() == "true"
WEB_DEFAULT_DEPTH = int(os.getenv("WEB_DEFAULT_DEPTH", "3"))
YOUTUBE_ALLOWED = os.getenv("YOUTUBE_ALLOWED", "true").lower() == "true"
YOUTUBE_DEFAULT_DEPTH = int(os.getenv("YOUTUBE_DEFAULT_DEPTH", "2"))

# LLM defaults
LLM_DEFAULT_TEMPERATURE = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.1"))
LLM_DEFAULT_MAX_TOKENS = int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "1024"))

# Database URL from .env (default fallback = SQLite local file)
DB_URL = os.getenv("DB_URL", "sqlite:///./app.db")
