import sys
import os
import json
# Ensure we can import from core
sys.path.append(os.getcwd())

from core.layer1_understanding.orchestrator import CVOrchestrator
from core.layer2_classification.classifier import CVDomainClassifier
from core.layer2_classification.domain_engine import DomainEngine
from core.layer2_classification.seniority_engine import SeniorityEngine
from core.layer2_classification.skill_engine import SkillEngine
from core.layer3_matching.job_description_engine import JobDescriptionEngine
from core.layer3_matching.similarity import IntelligentMatcher

def deep_trace_cv(pdf_path: str):
    print(f"\n[START] Starting Deep Trace for: {os.path.basename(pdf_path)}")
    print("="*60)

    # --- SETUP ENGINES ---
    classifier = CVDomainClassifier()
    embedder = classifier.embedder
    domain_engine = DomainEngine(classifier)
    seniority_engine = SeniorityEngine(embedder)
    skill_engine = SkillEngine()
    
    orchestrator = CVOrchestrator() # Layer 1 & 2
    
    # Layer 3
    jd_engine = JobDescriptionEngine(domain_engine, seniority_engine)
    matcher = IntelligentMatcher(embedder, domain_engine)

    # ---------------------------------------------------------
    # STEP 1: LAYER 1 (Understanding)
    # ---------------------------------------------------------
    print("\n[STEP 1] Layer 1: Spatial Understanding & Extraction")
    print("---------------------------------------------------------")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        
    result_raw = orchestrator.process_cv(pdf_bytes, filename=os.path.basename(pdf_path))
    # Deep convert to dict using JSON round-trip to handle Pydantic types like HttpUrl
    result = json.loads(result_raw.model_dump_json())
    
    raw_text_sample = result.get("profile", {}).get("summary", "No summary found")
    print(f"DONE: Text Extracted Successfully.")
    print(f"INFO: Summary Peek: {raw_text_sample[:150]}...")
    print(f"INFO: Full Name Detected: {result.get('profile', {}).get('full_name')}")

    # ---------------------------------------------------------
    # STEP 2: LAYER 2 (Classification)
    # ---------------------------------------------------------
    print("\n[STEP 2] Layer 2: Modular Classification (Engines)")
    print("---------------------------------------------------------")
    
    domain_scores = domain_engine.predict_domain(result)
    primary_domain = max(domain_scores, key=domain_scores.get)
    
    seniority_data = seniority_engine.analyze_seniority(result)
    
    cv_skills = result.get("skills", {}).get("items", [])
    skills_categorized = skill_engine.categorize_skills(cv_skills)
    
    # Get total years from Layer 1 metadata
    total_years = result.get("analysis", {}).get("metadata", {}).get("experience", {}).get("total_experience_years", 0.0)

    # Update result with Layer 2 info for matcher
    result["analysis"].update({
        "primary_domain": primary_domain,
        "seniority": seniority_data["level"],
        "domain_scores": domain_scores
    })

    print(f"RESULT: Domain Detected: {primary_domain} (Confidence: {domain_scores[primary_domain]:.2f})")
    print(f"RESULT: Seniority: {seniority_data['level']} (Years: {total_years})")
    print(f"RESULT: Top Hard Skills: {', '.join(skills_categorized['hard_skills'][:5])}")

    # ---------------------------------------------------------
    # STEP 3: LAYER 3 (Matchmaking)
    # ---------------------------------------------------------
    print("\n[STEP 3] Layer 3: Decision Intelligence Matchmaking")
    print("---------------------------------------------------------")
    
    target_jd = """
    Senior Software Engineer - Full Stack.
    Requirements:
    - 6+ years of experience.
    - Deep expertise in React and Node.js.
    - Experience with Cloud Infrastructure (AWS/Docker).
    - Strong communication and leadership skills.
    """
    
    print("INFO: Matching against JD: 'Senior Software Engineer (6+ years)'")
    
    parsed_jd = jd_engine.parse_jd(target_jd)
    match_report = matcher.calculate_match(result, parsed_jd)
    
    print(f"RESULT: Match Score: {match_report['match_score']}%")
    print(f"RESULT: Verdict: {match_report['fit_analysis']['verdict']}")
    
    print("\nFIT ANALYSIS BREAKDOWN:")
    print(f"STRENGTHS: {match_report['fit_analysis']['strengths']}")
    print(f"GAPS: {match_report['fit_analysis']['gaps']}")
    print(f"RED FLAGS: {match_report['fit_analysis']['red_flags']}")

    # Save Trace Output
    output_path = "tests/ahmed_abdelaziz_trace.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print(f"FINISH: Deep Trace Completed. Full JSON saved to {output_path}")

if __name__ == "__main__":
    cv_path = "tests/ahmedabdelaziz_resume.pdf"
    if os.path.exists(cv_path):
        deep_trace_cv(cv_path)
    else:
        print(f"File not found: {cv_path}")
