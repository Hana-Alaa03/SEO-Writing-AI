import re
from datetime import datetime
from typing import Optional

_YEAR_TOKEN = re.compile(r"\b(20\d{2})\b", re.IGNORECASE)
_YEAR_PLACEHOLDER = re.compile(r"\[year\]", re.IGNORECASE)

_FRESHNESS_KEYWORD_SIGNALS = (
    "افضل",
    "أفضل",
    "احسن",
    "أحسن",
    "best",
    "top",
    "leading",
    "rated",
    "أقوى",
    "اقوى",
    "ranking",
    "companies",
    "شركات",
    "شركة",
)


def current_calendar_year() -> str:
    return str(datetime.now().year)


def normalize_title_year(text: str, current_year: Optional[str] = None) -> str:
    """Replace any calendar year token or [year] placeholder with the current year."""
    if not text or not str(text).strip():
        return text
    year = current_year or current_calendar_year()
    normalized = _YEAR_PLACEHOLDER.sub(year, str(text))
    return _YEAR_TOKEN.sub(year, normalized).strip()


def keyword_implies_title_freshness(keyword: str) -> bool:
    kw = (keyword or "").lower()
    if _YEAR_TOKEN.search(kw) or "[year]" in kw:
        return True
    return any(signal in kw for signal in _FRESHNESS_KEYWORD_SIGNALS)


def title_needs_freshness_year(
    *,
    keyword: str = "",
    intent: str = "",
    content_type: str = "",
    raw_title: str = "",
) -> bool:
    if keyword_implies_title_freshness(keyword) or keyword_implies_title_freshness(raw_title):
        return True
    if _YEAR_TOKEN.search(raw_title or "") or "[year]" in (raw_title or "").lower():
        return True
    intent_l = (intent or "").lower()
    ctype = (content_type or "").lower()
    if intent_l in {"commercial", "commercial_comparative"} or ctype == "brand_commercial":
        return keyword_implies_title_freshness(keyword)
    return False


def finalize_article_title(
    title: str,
    *,
    keyword: str = "",
    intent: str = "",
    content_type: str = "",
    raw_title: str = "",
    current_year: Optional[str] = None,
) -> str:
    """Normalize stale years and ensure a freshness year for ranking/commercial titles."""
    year = current_year or current_calendar_year()
    title = normalize_title_year(title, year)
    if not title or not title_needs_freshness_year(
        keyword=keyword,
        intent=intent,
        content_type=content_type,
        raw_title=raw_title,
    ):
        return title
    if _YEAR_TOKEN.search(title):
        return title
    if " | " in title:
        head, tail = title.rsplit(" | ", 1)
        return f"{head} {year} | {tail}"
    return f"{title} {year}"


def enforce_meta_lengths(meta: dict) -> dict:
    """
    Ensures meta title respects SEO length rules.
    Meta description is kept as-is (no truncation).
    """

    title = meta.get("meta_title", "")
    description = meta.get("meta_description", "")

    # Only trim meta_title for SEO compliance
    meta["meta_title"] = title[:70]
    meta["meta_description"] = description  # No truncation

    return meta
