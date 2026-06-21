from typing import TypedDict, List, Dict, Any, Optional


class SerpData(TypedDict, total=False):
    top_results: List[Dict[str, Any]]
    paa_questions: List[str]
    related_searches: List[str]
    autocomplete_suggestions: List[str]
    lsi_keywords: List[str]
    intent: str
    serp_data_unavailable: bool
    serp_fallback_reason: str
    structural_stats: Dict[str, Any]
    serp_enrichment_sources: Dict[str, str]
    web_research_attempts: List[Dict[str, Any]]
    fallback_search_used: bool
    first_query: str
    fallback_query: str


class SectionDict(TypedDict, total=False):
    heading: str
    role: str
    section_page_narrative_briefs: List[Dict[str, Any]]
    section_brand_page_briefs: List[Dict[str, Any]]
    section_raw_brand_blocks: List[Dict[str, Any]]
    section_brand_understanding: Dict[str, Any]
    content: str
    word_count: int
    score: float
    requires_primary_keyword: bool
    heading_type: str


class StyleBlueprint(TypedDict, total=False):
    tone: str
    pov: str
    brand_voice_description: str
    brand_voice_guidelines: str
    brand_voice_examples: str
    custom_keyword_density: Optional[float]
    bold_key_terms: bool


class BrandEvidenceInventory(TypedDict, total=False):
    page_count: int
    total_services: int
    total_projects: int
    strong_signals: List[str]
    medium_signals: List[str]
    weak_signals: List[str]
    missing_evidence: List[str]


class WorkflowState(TypedDict, total=False):
    input_data: Dict[str, Any]
    primary_keyword: str
    content_type: str
    brand_name: str
    outline: List[SectionDict]
    article_language: str
    workflow_logger: Any
    display_brand_name: str
    brand_url: str
    brand_page_narrative_briefs: List[Dict[str, Any]]
    brand_page_knowledge_pack_context: str
    raw_title: str
    serp_data: SerpData
    seo_intelligence: Dict[str, Any]
    area: str
    content_strategy: str
    prohibited_competitors: List[str]
    serp_outline_brief: Dict[str, Any]
    brand_link_used: bool
    output_dir: str
    used_claims: List[str]
    final_output: str
    sections: List[SectionDict]
    used_external_links: List[Dict[str, str]]
    internal_resources: List[Dict[str, Any]]
    used_internal_links: List[Dict[str, str]]
    brand_evidence_failure_mode: str
    tone: str
    bold_key_terms: bool
    external_resources: List[Dict[str, str]]
    ctas_placed: int
    tables_placed: int
    heading_only_mode: bool
    used_anchors: List[str]
    introduction_text: str
    pov: str
    brand_evidence_inventory: BrandEvidenceInventory
    area_neighborhoods: List[str]
    style_blueprint: StyleBlueprint
    content_stage_only_mode: bool
    workflow_mode: str
    article_intent: str
    content_strategy_phase: str
    competitor_count: int
    web_research_attempts: List[Dict[str, Any]]
    fallback_search_used: bool
    llm_market_insights: str
    serp_thin: bool
    top_result_count: int
    brand_evidence_cards: List[Dict[str, Any]]
    brand_source_chunks: List[Dict[str, Any]]
    brand_crawl_report: Dict[str, Any]
    blocked_external_domains: set
    authority_domains: set
    used_topics: List[str]
    allowed_section_count: int
    generated_section_count: int
    brand_voice_description: str
    brand_voice_guidelines: str
    brand_voice_examples: str
    custom_keyword_density: Optional[float]
    num_images: int
    image_style: str
    image_size: str
    include_featured_image: bool
    max_external_links: int
    article_size: str
