"""
Export intermediate pipeline artifacts for evidence-based tracing (Sprint 0).

Neutral observability: records what each layer actually contained — no hardcoded
project preferences. The proof_trace matrix is built from GT catalog + runtime state.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_TRACE_ENTITY_LIMIT = 12


def _write_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")


def _mention_present(text: str, name: str) -> bool:
    if not text or not name:
        return False
    return name.casefold() in text.casefold()


def _projects_from_gt(state: Dict[str, Any]) -> List[str]:
    """Collect project names observed in ground truth / knowledge pack (neutral order)."""
    names: List[str] = []
    seen = set()

    def add(value: Any) -> None:
        name = re.sub(r"\s+", " ", str(value or "")).strip()
        if not name or len(name) < 2:
            return
        key = name.casefold()
        if key in seen:
            return
        seen.add(key)
        names.append(name)

    try:
        from src.services.brand_evidence_service import build_brand_evidence_cards, _collect_card_values, _filter_derived_project_catalog

        cards = state.get("brand_evidence_cards") or []
        if not cards and state.get("internal_resources"):
            cards = build_brand_evidence_cards(state)
        projects = _filter_derived_project_catalog(
            _collect_card_values(cards, ["visible_project_or_case_study_examples"], limit=24, category="project")
        )
        for proj in projects:
            add(proj)
    except Exception as exc:
        logger.debug("GT project catalog unavailable for trace: %s", exc)

    for brief in state.get("brand_page_narrative_briefs") or []:
        if not isinstance(brief, dict):
            continue
        title = brief.get("page_title") or ""
        if " - " in title:
            add(title.split(" - ")[0].strip())
        for proj in brief.get("observed_projects") or []:
            add(proj)

    pack_path = os.path.join(state.get("output_dir") or "", "brand_ground_truth.md")
    if os.path.isfile(pack_path):
        try:
            with open(pack_path, "r", encoding="utf-8") as f:
                gt_md = f.read()
            for match in re.finditer(r"^### Page \d+: (.+?) - ", gt_md, re.MULTILINE):
                add(match.group(1).strip())
        except OSError:
            pass

    return names[:_TRACE_ENTITY_LIMIT]


def _strategy_proof_strings(state: Dict[str, Any]) -> List[str]:
    strategy = state.get("content_strategy") or {}
    points = strategy.get("supported_proof_points") or []
    return [str(p).strip() for p in points if str(p).strip()]


def _outline_proof_sections(outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    proof_sections = []
    for section in outline or []:
        if not isinstance(section, dict):
            continue
        section_type = str(section.get("section_type") or "").lower()
        role = str(section.get("commercial_section_role") or "").lower()
        heading = str(section.get("heading_text") or "")
        is_proof = (
            section_type in {"proof", "case_study", "authority"}
            or role == "proof"
            or any(token in heading for token in ("مشاريع", "أعمال", "portfolio", "case stud", "proof"))
        )
        if is_proof:
            proof_sections.append(
                {
                    "section_id": section.get("section_id"),
                    "heading_text": heading,
                    "section_type": section_type,
                    "commercial_section_role": role,
                    "subheadings": section.get("subheadings", []),
                }
            )
    return proof_sections


def _extract_section_markdown(final_markdown: str, section_id: str) -> str:
    """Return body text for a section_id marker in assembled article markdown."""
    if not final_markdown or not section_id:
        return ""
    marker = re.search(
        rf"<!--\s*section_id:\s*{re.escape(section_id)}\s*-->",
        final_markdown,
        re.IGNORECASE,
    )
    if not marker:
        return ""
    start = marker.end()
    tail = final_markdown[start:]
    next_boundary = re.search(r"(?m)^#{2,6}\s+|<!--\s*section_id:\s*", tail)
    end = start + next_boundary.start() if next_boundary else len(final_markdown)
    return final_markdown[start:end].strip()


def _required_names_from_section(section: Dict[str, Any]) -> List[str]:
    names = section.get("required_project_names")
    if not names:
        contract = section.get("section_contract") or {}
        names = contract.get("required_project_names")
    return [
        re.sub(r"\s+", " ", str(name)).strip()
        for name in (names or [])
        if re.sub(r"\s+", " ", str(name)).strip()
    ]


def _build_required_names_validation(
    outline: List[Dict[str, Any]],
    sections: Dict[str, Any],
    final_markdown: str,
) -> Dict[str, Any]:
    """Sprint 1-C: validate required project names appear in the proof section only."""
    proof_sections = _outline_proof_sections(outline)
    if not proof_sections:
        return {
            "proof_section_id": None,
            "required_project_names": [],
            "required_names_in_proof_section": None,
            "missing_required_names": [],
        }

    primary = proof_sections[0]
    section_id = str(primary.get("section_id") or "")
    section = next(
        (item for item in outline if isinstance(item, dict) and item.get("section_id") == section_id),
        {},
    )
    required_names = _required_names_from_section(section)
    if not required_names:
        return {
            "proof_section_id": section_id or None,
            "required_project_names": [],
            "required_names_in_proof_section": None,
            "missing_required_names": [],
        }

    proof_content = ""
    if isinstance(sections, dict) and section_id:
        sec_data = sections.get(section_id) or {}
        if isinstance(sec_data, dict):
            proof_content = str(sec_data.get("generated_content") or "")
    if not proof_content and final_markdown:
        proof_content = _extract_section_markdown(final_markdown, section_id)

    missing = [name for name in required_names if not _mention_present(proof_content, name)]
    return {
        "proof_section_id": section_id or None,
        "required_project_names": required_names,
        "required_names_in_proof_section": not missing,
        "missing_required_names": missing,
    }


def _layer_hit(text: str, entity: str) -> bool:
    return _mention_present(text, entity)


def _build_entity_row(
    entity: str,
    *,
    gt: bool,
    strategy_text: str,
    outline_text: str,
    contract_text: str,
    writer_prompt: str,
    writer_output: str,
    article_text: str,
) -> Dict[str, Any]:
    return {
        "entity": entity,
        "gt": gt,
        "strategy": _layer_hit(strategy_text, entity),
        "outline": _layer_hit(outline_text, entity),
        "contract": _layer_hit(contract_text, entity),
        "writer_prompt": _layer_hit(writer_prompt, entity),
        "writer_output": _layer_hit(writer_output, entity),
        "article": _layer_hit(article_text, entity),
    }


def export_pipeline_trace_artifacts(
    state: Dict[str, Any],
    *,
    final_markdown: str = "",
    controller: Any = None,
) -> Optional[str]:
    """
    Persist tracing JSON/MD files under output_dir. Returns proof_trace path or None.
    """
    output_dir = str(state.get("output_dir") or "").strip()
    if not output_dir:
        logger.warning("[pipeline_trace] output_dir missing; skipping artifact export.")
        return None

    os.makedirs(output_dir, exist_ok=True)

    content_strategy = state.get("content_strategy") or {}
    outline = state.get("outline") or []
    sections = state.get("sections") or {}

    section_contracts = []
    for section in outline:
        if not isinstance(section, dict):
            continue
        sid = section.get("section_id")
        generated = sections.get(sid, {}) if isinstance(sections, dict) else {}
        merged = dict(section)
        if isinstance(generated, dict):
            merged["generated_content_preview"] = str(generated.get("generated_content") or "")[:500]
        section_contracts.append(
            {
                "section_id": sid,
                "heading_text": section.get("heading_text"),
                "section_type": section.get("section_type"),
                "commercial_section_role": section.get("commercial_section_role"),
                "required_project_names": section.get("required_project_names")
                or (section.get("section_contract") or {}).get("required_project_names")
                or [],
                "section_contract": section.get("section_contract") or {},
                "safe_project_records_from_pack": section.get("safe_project_records_from_pack")
                or generated.get("safe_project_records_from_pack")
                or [],
                "writer_truth_trace": section.get("writer_truth_trace")
                or generated.get("writer_truth_trace"),
            }
        )

    _write_json(os.path.join(output_dir, "content_strategy.json"), content_strategy)
    _write_json(os.path.join(output_dir, "outline.json"), outline)
    _write_json(os.path.join(output_dir, "section_contracts.json"), section_contracts)

    proof_sections = _outline_proof_sections(outline)
    primary_proof_id = None
    if proof_sections:
        primary_proof_id = proof_sections[0].get("section_id")
    else:
        for section in outline:
            if isinstance(section, dict) and section.get("section_id"):
                primary_proof_id = section.get("section_id")
                break

    writer_prompt_blob = ""
    writer_output_blob = ""
    if primary_proof_id and isinstance(sections, dict):
        sec_data = sections.get(primary_proof_id) or {}
        for section in outline:
            if section.get("section_id") == primary_proof_id:
                writer_prompt_blob = str(
                    section.get("writer_prompt_text")
                    or sec_data.get("writer_prompt_text")
                    or ""
                )
                writer_output_blob = str(
                    sec_data.get("generated_content")
                    or section.get("writer_response_text")
                    or section.get("generated_content")
                    or ""
                )
                break

        payload_path = os.path.join(output_dir, f"writer_payload_{primary_proof_id}.json")
        _write_json(
            payload_path,
            {
                "section_id": primary_proof_id,
                "heading_text": next(
                    (s.get("heading_text") for s in outline if s.get("section_id") == primary_proof_id),
                    "",
                ),
                "prompt_chars": len(writer_prompt_blob),
                "prompt_text": writer_prompt_blob,
            },
        )
        _write_text(
            os.path.join(output_dir, f"writer_output_{primary_proof_id}.md"),
            writer_output_blob,
        )

    for section in outline:
        if not isinstance(section, dict):
            continue
        sid = str(section.get("section_id") or "")
        if not sid:
            continue
        role = str(section.get("commercial_section_role") or "").lower()
        stype = str(section.get("section_type") or "").lower()
        if role != "proof" and stype not in {"proof", "case_study"}:
            continue
        sec_data = sections.get(sid, {}) if isinstance(sections, dict) else {}
        prompt_text = str(section.get("writer_prompt_text") or sec_data.get("writer_prompt_text") or "")
        output_text = str(sec_data.get("generated_content") or "")
        _write_json(
            os.path.join(output_dir, f"writer_payload_{sid}.json"),
            {
                "section_id": sid,
                "heading_text": section.get("heading_text"),
                "prompt_chars": len(prompt_text),
                "prompt_text": prompt_text,
            },
        )
        _write_text(os.path.join(output_dir, f"writer_output_{sid}.md"), output_text)

    strategy_text = json.dumps(content_strategy, ensure_ascii=False)
    outline_text = json.dumps(outline, ensure_ascii=False)
    contract_text = json.dumps(section_contracts, ensure_ascii=False)

    # Ranked pack records (what proof gate would see) — neutral, from narrative pack
    ranked_records: List[Dict[str, Any]] = []
    if controller is not None:
        try:
            proof_section = next(
                (s for s in outline if str(s.get("commercial_section_role") or "").lower() == "proof"),
                None,
            ) or next(
                (s for s in outline if str(s.get("section_type") or "").lower() == "proof"),
                None,
            )
            ranked_records = controller._project_records_from_narrative_pack(
                state,
                proof_section,
                limit=8,
            )
        except Exception as exc:
            logger.debug("[pipeline_trace] ranked project records unavailable: %s", exc)

    gt_projects = _projects_from_gt(state)
    trace_entities = list(dict.fromkeys(gt_projects + [r.get("name") for r in ranked_records if r.get("name")]))[
        :_TRACE_ENTITY_LIMIT
    ]

    matrix = [
        _build_entity_row(
            entity,
            gt=entity in gt_projects,
            strategy_text=strategy_text,
            outline_text=outline_text,
            contract_text=contract_text,
            writer_prompt=writer_prompt_blob,
            writer_output=writer_output_blob,
            article_text=final_markdown,
        )
        for entity in trace_entities
    ]

    process_steps_gt = []
    for brief in state.get("brand_page_narrative_briefs") or []:
        if not isinstance(brief, dict):
            continue
        for step in brief.get("observed_process_steps") or []:
            step_name = str(step).strip()
            if step_name and step_name not in process_steps_gt:
                process_steps_gt.append(step_name)

    faq_h3_count = len(re.findall(r"(?m)^#{3,6}\s+", final_markdown or ""))

    required_names_validation = _build_required_names_validation(outline, sections, final_markdown)

    proof_trace = {
        "mode": "content_stage_only" if state.get("content_stage_only_mode") else "full_pipeline",
        "primary_keyword": state.get("primary_keyword"),
        "target_area": state.get("area"),
        "gt_project_catalog": gt_projects,
        "strategy_supported_proof_points": _strategy_proof_strings(state),
        "outline_proof_sections": proof_sections,
        "ranked_project_records_from_pack": ranked_records,
        "entity_trace_matrix": matrix,
        "required_names_validation": required_names_validation,
        "process_trace": {
            "gt_observed_steps": process_steps_gt[:12],
            "in_strategy": _layer_hit(strategy_text, "process") or bool(process_steps_gt),
            "in_outline": any(
                str(s.get("section_type") or "").lower() in {"process", "process_or_how"}
                or str(s.get("commercial_section_role") or "").lower() == "process"
                for s in outline
                if isinstance(s, dict)
            ),
            "in_article": bool(re.search(r"(?m)^#{3,6}\s+.*(?:خطو|مرحل|استشار|تصميم|تطوير|اختبار|تسليم)", final_markdown or "")),
        },
        "faq_trace": {
            "serp_faq_ratio": (state.get("seo_intelligence") or {}).get("market_analysis", {})
            .get("structural_intelligence", {})
            .get("faq_presence_ratio"),
            "outline_faq_section": any(
                str(s.get("section_type") or "").lower() == "faq" for s in outline if isinstance(s, dict)
            ),
            "article_h3_count": faq_h3_count,
        },
        "artifact_files": [
            "content_strategy.json",
            "outline.json",
            "section_contracts.json",
            "proof_trace.json",
            f"writer_payload_{primary_proof_id}.json" if primary_proof_id else None,
            f"writer_output_{primary_proof_id}.md" if primary_proof_id else None,
        ],
    }
    proof_trace["artifact_files"] = [f for f in proof_trace["artifact_files"] if f]

    trace_path = os.path.join(output_dir, "proof_trace.json")
    _write_json(trace_path, proof_trace)

    if final_markdown:
        _write_text(os.path.join(output_dir, "article_final.md"), final_markdown)

    logger.info("[pipeline_trace] Exported tracing artifacts to %s", output_dir)
    return trace_path
