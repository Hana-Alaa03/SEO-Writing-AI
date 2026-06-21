import logging
import os
from typing import Dict, Any
from jinja2 import Template, StrictUndefined
from src.services.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "prompts", "templates")

class ArticleRefiner:
    def __init__(self, ai_client: OpenRouterClient):
        self.ai_client = ai_client
        with open(os.path.join(_TEMPLATES_DIR, "09_article_refiner.txt"), "r", encoding="utf-8") as f:
            self.template = Template(f.read(), undefined=StrictUndefined)

    async def refine(self, markdown: str, metadata: Dict[str, Any]) -> str:
        prompt = self.template.render(
            markdown=markdown,
            metadata=metadata
        )
        res = await self.ai_client.send(prompt, step="refine")
        return res["content"]
