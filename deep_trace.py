"""
Deep Layer-by-Layer Trace Script
=================================
Runs the CV through each pipeline stage separately and prints the exact
output of every layer to a JSON file: tests/deep_trace_output.json
"""
import io
import json
import re
import sys
import os
from pathlib import Path
from statistics import median

# Make sure imports work from the project root
sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"e:\flutter_projects\Graduation-project\ai-cv-analyzer\tests\Flutter Developer_CV_Ahmed_Khames .pdf.pdf"
OUT_PATH  = r"e:\flutter_projects\Graduation-project\ai-cv-analyzer\tests\deep_trace_output.json"

pdf_bytes = Path(PDF_PATH).read_bytes()
print(f"[✓] PDF loaded: {len(pdf_bytes)/1024:.1f} KB")

trace = {}

# ─────────────────────────────────────────────────────────────────
# LAYER 1 — UNDERSTANDING
# ─────────────────────────────────────────────────────────────────

# ── Step 1a: Spatial Parser ──────────────────────────────────────
print("[→] Layer 1 / Step 1: Spatial Parser ...")
from core.layer1_understanding.spatial_parser import extract_spatial_text_from_pdf
spatial = extract_spatial_text_from_pdf(pdf_bytes)

raw_text_with_hints = spatial.text or ""
clean_text = re.sub(r'^\[H\] ', '', raw_text_with_hints, flags=re.MULTILINE)

# Count how many lines got [H] tag (= header candidates by font size)
lines_with_h = [ln for ln in raw_text_with_hints.splitlines() if ln.startswith("[H] ")]

trace["layer1_step1_spatial_parser"] = {
    "status": spatial.status,
    "page_count": spatial.page_count,
    "word_count": spatial.word_count,
    "char_count": len(clean_text),
    "font_header_candidates_detected": len(lines_with_h),
    "font_header_lines": [ln[4:] for ln in lines_with_h],   # strip [H] for display
    "raw_text_preview": clean_text[:600] + "...",
}
print(f"  pages={spatial.page_count}, words={spatial.word_count}, font-headers={len(lines_with_h)}")

# ── Step 1b: Section Segmenter ───────────────────────────────────
print("[→] Layer 1 / Step 2: Section Segmenter ...")
from core.layer1_understanding.section_segmenter import SemanticSegmenter

# Use the text WITH [H] hints so the segmenter can exploit them
segmenter = SemanticSegmenter()   # no embedder for this trace (faster)
segments  = segmenter.segment(raw_text_with_hints)

trace["layer1_step2_section_segmenter"] = {
    "found_sections": list(segments.analysis.found_sections),
    "sections_missing": list(segments.analysis.sections_missing),
    "anomalies": list(segments.analysis.anomalies),
    "header_hits": [
        {"line_idx": h[0], "text": h[1], "section": h[2], "confidence": round(h[3], 2)}
        for h in segments.analysis.header_hits
    ],
    "sections_text": {k: v[:300] + ("..." if len(v) > 300 else "") for k, v in segments.sections.items()},
}
print(f"  found={list(segments.analysis.found_sections)}")

# ── Step 1c: Contact Extractor ───────────────────────────────────
print("[→] Layer 1 / Step 3: Contact Extractor ...")
from core.layer1_understanding.contact_extractor import extract_contacts
contacts = extract_contacts(clean_text)
trace["layer1_step3_contact_extractor"] = contacts
print(f"  email={contacts.get('email')}, phone={contacts.get('phone')}, location={contacts.get('location')}")

# ── Step 1d: NER Engine ──────────────────────────────────────────
print("[→] Layer 1 / Step 4: NER Engine ...")
from core.layer1_understanding.advanced_ner import AdvancedNEREngine
ner = AdvancedNEREngine()
entities = ner.extract_entities(clean_text, context_window_words=3)
name_candidate = ner.extract_candidate_name(
    segments.sections.get("profile_summary", clean_text[:500]),
    entities
)
trace["layer1_step4_ner"] = {
    "name_candidate": {
        "full_name": name_candidate.full_name if name_candidate else None,
        "confidence": round(name_candidate.confidence_score, 2) if name_candidate else 0,
    },
    "roles_found": entities.get("roles", []),
    "orgs_found": entities.get("orgs", []),
    "locations_found": entities.get("locations", []),
    "skills_found": entities.get("skills", []),
    "skills_count": len(entities.get("skills", [])),
}
print(f"  name={name_candidate.full_name if name_candidate else 'N/A'}, roles={entities.get('roles', [])[:3]}")

# ── Step 1e: Canonicalizer ───────────────────────────────────────
print("[→] Layer 1 / Step 5: Canonicalizer ...")
from core.layer1_understanding.canonicalizer import DataCanonicalizer
canon = DataCanonicalizer(fuzzy_threshold=86)
raw_skills = entities.get("skills", [])
canonical_skills = canon.canonicalize_skills(raw_skills, skill_confidence=0.65, source="ner")
trace["layer1_step5_canonicalizer"] = {
    "raw_skills_in": raw_skills,
    "canonical_skills_out": [{"name": s.name, "confidence": round(s.confidence_score, 2)} for s in canonical_skills],
    "deduplication_removed": len(raw_skills) - len(canonical_skills),
}
print(f"  raw_skills={len(raw_skills)} → canonical={len(canonical_skills)}")

# ── Step 1f: Experience Engine ───────────────────────────────────
print("[→] Layer 1 / Step 6: Experience Engine ...")
from core.layer1_understanding.experience_engine import ExperienceEngine
exp_engine = ExperienceEngine()
exp_text = segments.sections.get("experience", "")
date_ranges = exp_engine.extract_date_ranges(exp_text)
total_years = exp_engine.calculate_total_experience_years(exp_text)
trace["layer1_step6_experience_engine"] = {
    "experience_text_preview": exp_text[:300] + "..." if len(exp_text) > 300 else exp_text,
    "date_ranges_found": [
        {"start": str(r.start), "end": str(r.end), "source_text": r.source_text}
        for r in date_ranges
    ],
    "total_experience_years": round(total_years, 2),
}
print(f"  date_ranges={len(date_ranges)}, total_years={total_years:.1f}")

# ─────────────────────────────────────────────────────────────────
# LAYER 2 — CLASSIFICATION
# ─────────────────────────────────────────────────────────────────
print("[→] Layer 2: Domain Classifier ...")
try:
    from core.layer2_classification.classifier import CVDomainClassifier
    classifier = CVDomainClassifier()
    cv_data_for_classifier = {
        "skills": {"items": [{"name": s.name} for s in canonical_skills]},
        "experience": {"items": [{"title": "Junior Flutter Developer", "technologies": ["Flutter", "Firebase"]}]},
        "analysis": {"metadata": {"extraction": {"raw_text": clean_text}}}
    }
    domain_scores = classifier.predict_domain_from_cv_data(cv_data_for_classifier)
    primary_domain = max(domain_scores, key=domain_scores.get) if domain_scores else None
    trace["layer2_domain_classifier"] = {
        "primary_domain": primary_domain,
        "all_scores": {k: round(v, 3) for k, v in sorted(domain_scores.items(), key=lambda x: -x[1])},
        "top_3": [{"domain": k, "score": round(v, 3)} for k, v in sorted(domain_scores.items(), key=lambda x: -x[1])[:3]],
        "issue": "⚠️ 'Customer Service' ranked #1 despite strong Flutter/Mobile skills — classifier needs domain-weight tuning."
    }
    print(f"  primary_domain={primary_domain}")
except Exception as e:
    trace["layer2_domain_classifier"] = {"error": str(e)}
    print(f"  ERROR: {e}")

# ─────────────────────────────────────────────────────────────────
# LAYER 3 — MATCHING (requires a sample job description)
# ─────────────────────────────────────────────────────────────────
print("[→] Layer 3: Similarity Matcher ...")
try:
    from core.layer3_matching.similarity import IntelligentMatcher
    matcher = IntelligentMatcher()

    sample_cv_data = {
        "skills": {"items": [{"name": s.name} for s in canonical_skills]},
        "experience": {
            "items": [{"title": "Junior Flutter Developer", "technologies": ["Flutter", "Firebase", "Dart"]}],
            "confidence_score": 0.85
        },
        "analysis": {
            "seniority": "junior",
            "primary_domain": primary_domain,
            "predicted_role": "Junior Flutter Developer",
        }
    }
    sample_job = {
        "title": "Flutter Mobile Developer",
        "required_skills": ["Flutter", "Dart", "Firebase", "REST APIs", "Git"],
        "preferred_skills": ["Bloc", "Clean Architecture", "Provider"],
        "description": "We need a junior Flutter developer with Firebase experience and strong UI skills.",
        "seniority_level": "junior",
        "domain": "Technology & Software",
    }

    match_result = matcher.match(cv_data=sample_cv_data, job_data=sample_job)
    trace["layer3_matching"] = {
        "sample_job_title": sample_job["title"],
        "overall_score": round(match_result.get("overall_score", 0), 3),
        "skill_match_score": round(match_result.get("skill_score", 0), 3),
        "seniority_match": match_result.get("seniority_match"),
        "matched_skills": match_result.get("matched_skills", []),
        "missing_skills": match_result.get("missing_skills", []),
        "recommendation": match_result.get("recommendation", ""),
    }
    print(f"  overall_score={match_result.get('overall_score', 0):.2f}")
except Exception as e:
    trace["layer3_matching"] = {"error": str(e), "note": "Layer 3 requires a job description to match against — no error if skipped here."}
    print(f"  Layer 3 note: {e}")

# ─────────────────────────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────────────────────────
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(trace, f, ensure_ascii=False, indent=2, default=str)

print(f"\n[✓] Deep trace complete → {OUT_PATH}")
