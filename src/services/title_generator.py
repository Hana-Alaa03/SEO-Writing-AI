import logging
import re
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from jinja2 import Template, StrictUndefined
from src.utils.json_utils import recover_json
from src.utils.seo_utils import finalize_article_title, normalize_title_year

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "prompts", "templates")

class TitleGenerator:
    def __init__(self, ai_client: Any, template_path: str = None):
        self.ai_client = ai_client
        if template_path is None:
            template_path = os.path.join(_TEMPLATES_DIR, "00_seo_intent_title.txt")
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = Template(f.read(), undefined=StrictUndefined)

    async def generate(
        self, 
        raw_title: str, 
        primary_keyword: str, 
        article_language: str,
        serp_titles: Optional[List[str]] = None,
        serp_cta_styles: Optional[List[str]] = None,
        area: Optional[str] = None,
        brand_name: str = "",
        serp_confirmed_intent: str = "",
        serp_intent_confidence: float = 0.0,
    ) -> Dict[str, Any]:

        current_year = str(datetime.now().year)
        processed_raw_title = normalize_title_year(raw_title, current_year)

        prompt = self.template.render(
            raw_title=processed_raw_title,
            primary_keyword=primary_keyword,
            article_language=article_language,
            serp_titles=serp_titles or [],
            serp_cta_styles=serp_cta_styles or [],
            area=area,
            brand_name=brand_name,
            serp_confirmed_intent=serp_confirmed_intent,
            serp_intent_confidence=serp_intent_confidence,
            current_year=current_year
        )

        logger.info("\n==== FINAL PROMPT (TitleGenerator) ====\n")
        logger.info(prompt)
        logger.info("\n======================================\n")

        res = await self.ai_client.send(prompt, step="title")
        raw_response = res["content"]
        data = recover_json(raw_response) or {}
        
        title = data.get("optimized_title", processed_raw_title)
        intent = data.get("intent", "Informational")

        if title:
            title = self._cleanup_title(title, primary_keyword, area, intent, current_year)
            title = finalize_article_title(
                title,
                keyword=primary_keyword,
                intent=intent,
                raw_title=processed_raw_title,
                current_year=current_year,
            )

        return {
            "optimized_title": title.strip(),
            "intent": intent.strip(),
            "metadata": res["metadata"],
            "prompt": prompt
        }

    def _cleanup_title(self, title: str, keyword: str, area: Optional[str], intent: str, year: str) -> str:
        """Removes unwanted localization and year injection for conceptual topics."""
        if not title:
            return ""

        title = normalize_title_year(title, year)

        # Step 2: Detect if topic is conceptual/educational
        is_conceptual = str(intent).lower() in ["informational", "educational_comparative"]
        
        # Check if keyword has local intent
        keyword_lower = keyword.lower()
        has_local_intent = False
        if area:
            area_lower = area.lower()
            if area_lower in keyword_lower or any(word in keyword_lower for word in ["in", "near", "في", "بجوار", "قرب"]):
                has_local_intent = True

        # Check if keyword has year intent
        has_year_intent = year in keyword_lower or "[year]" in keyword_lower

        if is_conceptual:
            # Remove year if not explicitly requested
            if not has_year_intent:
                # Remove year if it's at the end with a separator or just standalone
                title = re.sub(rf"\s*[-|:]?\s*{year}\b", "", title).strip()
                title = re.sub(rf"\b{year}\s*[-|:]?\s*", "", title).strip()

            # Remove localization if not explicitly requested
            if not has_local_intent and area:
                # Common patterns for "in [Area]" or "[Area] market"
                patterns = [
                    rf"\s*في\s*{area}",
                    rf"\s*داخل\s*{area}",
                    rf"\s*بالقرب\s*من\s*{area}",
                    rf"\s*السوق\s*ال{area}\w*", 
                    rf"\s*in\s*{area}",
                    rf"\s*near\s*{area}",
                    rf"\s*{area}\s*market",
                ]
                
                # Also handle common generic Arabic area patterns if area is "Egypt"
                if area in ["Egypt", "مصر"]:
                    patterns.extend([
                        r"\s*في\s*مصر",
                        r"\s*داخل\s*مصر",
                        r"\s*السوق\s*المصري",
                    ])

                for pattern in patterns:
                    title = re.sub(pattern, "", title, flags=re.IGNORECASE).strip()

        # Clean up any resulting double spaces or trailing separators
        title = re.sub(r"\s+", " ", title)
        title = re.sub(r"[:\-|\s]+$", "", title).strip()
        
        return title
