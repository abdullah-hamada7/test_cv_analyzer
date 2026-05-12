import os
import json
import sys

# Ensure we can import from core
sys.path.append(os.getcwd())

from core.layer1_understanding.orchestrator import CVOrchestrator
from core.layer1_understanding.spatial_parser import extract_spatial_text_from_pdf
from core.layer1_understanding.ocr_pipeline import OCR_AVAILABLE, extract_images_from_pdf_bytes, extract_text_from_image

def trace_up_to_ner(pdf_path: str):
    print(f"Processing: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    orchestrator = CVOrchestrator()
    
    # 1. Extraction (Spatial)
    spatial = extract_spatial_text_from_pdf(pdf_bytes)
    text = spatial.text or ""
    
    # Check if OCR fallback is needed (mimicking orchestrator)
    if not text or len(text) < 150:
        print("Triggering OCR Fallback...")
        if OCR_AVAILABLE:
            images = extract_images_from_pdf_bytes(pdf_bytes)
            ocr_parts = []
            for img in images:
                ocr_parts.append(extract_text_from_image(img))
            text = "\n\n".join(ocr_parts)
        else:
            print("OCR not available.")

    # 2. Segmentation
    segments = orchestrator._segmenter.segment(text)
    
    # 3. NER
    entities = orchestrator._ner.extract_entities(text)
    
    # 4. Name Candidate (Final step before full NLP pipeline continues)
    profile_text = segments.sections.get("profile_summary") or segments.sections.get("uncategorized") or text
    name_candidate = orchestrator._ner.extract_candidate_name(profile_text, entities)
    
    output = {
        "raw_text": text,
        "segments": {
            "found_sections": list(segments.analysis.found_sections),
            "sections": segments.sections
        },
        "ner_entities": entities,
        "candidate_name": {
            "full_name": name_candidate.full_name if name_candidate else None,
            "confidence": name_candidate.confidence_score if name_candidate else 0.0
        }
    }
    
    output_file = "tests/ner_trace_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    cv_path = r"e:\flutter_projects\Graduation-project\ai-cv-analyzer\tests\Flutter Developer_CV_Ahmed_Khames .pdf.pdf"
    if os.path.exists(cv_path):
        trace_up_to_ner(cv_path)
    else:
        print(f"File not found: {cv_path}")
