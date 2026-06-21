# Code-Level Technical Bugs (Not in PDF Report)

| # | Issue | File / Location |
|---|-------|-----------------|
| 1 | **Duplicate class definitions** - `_enforce_paragraph_word_limit`, `OutlineGenerator`, `SectionWriter` defined twice (lines 1-216 duplicated) | `src/services/content_generator.py` |
| 2 | **Circular import** - `api.py` imports from itself: `from src.app.api import app` | `src/app/api.py:11` |
| 3 | **Hardcoded relative template paths** - `FileSystemLoader("assets/prompts/templates")` breaks when CWD ≠ project root | `src/services/workflow_controller.py:181`, `content_generator.py:107,223`, `research_service.py:640,729,783,970` |
| 4 | **State mutation on failed steps** - `state = result.get("data", state)` updates state even when step fails (non-critical) | `src/services/workflow_controller.py:330` |
| 5 | **Language detection race condition** - API auto-detects from title regex vs Strategy service uses `langdetect` with 0.70 threshold | `src/app/api.py:162-168` vs `src/services/strategy_service.py:313-348` |
| 6 | **`content_stage_only_mode` logic bug** - Skips assembly entirely instead of stopping after content writing | `src/services/workflow_controller.py:295-318` |
| 7 | **Heading-only mode early stop** - Breaks loop without running `_assemble_final_output` properly | `src/services/workflow_controller.py:346-349` |
| 8 | **Pricing extraction regex fails on Arabic-Indic digits** - Misses `١٠٠٬٠٠٠`, `110K`, `1.1M` formats | `src/services/workflow_controller.py:1290` |
| 9 | **Link sanitization triple-processing** - 3 passes (`sanitize_section_links`, `sanitize_links`, `deduplicate_links_in_markdown`) cause drift | `src/utils/link_manager.py:89,164,224` |
| 10 | **ValidationService state leakage** - Shared instance mutates `self.is_property_domain` across requests | `src/services/validation_service.py:150,155` |
| 11 | **No request timeout config / circuit breaker** - Hardcoded 40s timeout, no per-step differentiation | `src/services/openrouter_client.py:41` |
| 12 | **Security: Full traceback in API response** - Returns internal stack traces to client | `src/app/api.py:369-372` |
| 13 | **Security: CORS allows all origins** - `allow_origins=["*"]` in production | `src/app/api.py:49` |
| 14 | **Security: File upload without type validation** - Arbitrary file write to `output/uploads/` | `src/app/api.py:193-230` |
| 15 | **Dead code / unused imports** - `detect_langs`, `Counter`, `PIL.Image`, duplicate blocks | `workflow_controller.py:26,32`, `research_service.py:15`, `content_generator.py:117-216` |
| 16 | **Hardcoded model names in config** - `gpt-4.1`, `o4-mini:online`, `gemini-3.1-flash-image-preview` not env-configurable | `src/config/ai_config.py:23,28,32` |
| 17 | **No typed state schema (Pydantic)** - 100+ state keys with no validation, typos cause silent failures | Across all services |
| 18 | **pytest not in requirements** - 50+ test files but no test runner dependency | `requirements.txt` / `pyproject.toml` (missing) |