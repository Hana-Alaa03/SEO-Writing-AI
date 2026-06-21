"""
Single source of truth for all AI providers.
"""

import os
from openai import OpenAI

from src.config.env_loader import load_project_env

load_project_env()


def _env(key: str, default: str = None) -> str | None:
    val = os.getenv(key, default)
    return val.strip() if isinstance(val, str) else val

# =========================
# TEXT MODELS
# =========================
OPENROUTER = {
    "api_key": _env("OPENROUTER_API_KEY"),
    "base_url_chat": "https://openrouter.ai/api/v1/chat/completions",
    "base_url_responses": "https://openrouter.ai/api/v1/responses",
    "base_url_image": "https://openrouter.ai/api/v1/chat/completions",
    "site_url": "https://github.com/Start-SE/SEO-Writing-AI",
    "site_name": "SEO Writing AI",

    "models": {
        "writing": os.getenv("AI_MODEL_WRITING", "openai/gpt-4.1"),
        "research": os.getenv("AI_MODEL_RESEARCH", "openai/o4-mini:online"),
        "image": os.getenv("AI_MODEL_IMAGE", "google/gemini-3.1-flash-image-preview")
    }
}

AGENTROUTER = {
    "api_key": os.getenv("AGENTROUTER_API_KEY"),
    "base_url": os.getenv("AGENTROUTER_BASE_URL", "https://agentrouter.org/v1"),
    "site_url": "https://github.com/Start-SE/SEO-Writing-AI",
    "site_name": "SEO Writing AI",
    "models": {
        "writing": os.getenv("AGENTROUTER_MODEL_WRITING", "claude-haiku-4-5-20251001")
    }
}

GROQ = {
    "enabled": True,
    "api_key": os.getenv("GROQ_API_KEY"),
    "default_model": "llama-3.3-70b-versatile",
    "max_tokens": {
        "outline": 800,
        "section": 1200,
        "image": 300,
        "assembly": 700,
        "default": 700
    }
}

# =========================
# IMAGE MODELS
# =========================
POLLINATIONS = {
    "model": "stable-diffusion",
    "size": "1024x1024",
    "base_url": "https://image.pollinations.ai/prompt"
}

STABILITY = {
    "api_key": "STABILITY_API_KEY",
    "model": "stable-diffusion-xl-1024-v1-0",
    "base_url": "https://api.stability.ai/v1/generation",
    "size": "1024x1024"
}


IMAGES = {
    "provider": "mock"  
}


# config.py
STRUCTURE_RULES = {
    "informational": {
        "required_h2": [
            "Pros",
            "Cons",
            "Who is it for?",
            "Who should avoid it?",
            "Alternatives"
        ],
        "faq_required": True,
        "conclusion_required": True
    },
    "brand_commercial": {
        "benefits_required": True,
        "faq_required": False,
        "strong_cta_first_core": True
    }
}
