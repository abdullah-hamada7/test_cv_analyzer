import sys
import os
import json
# Ensure we can import from core
sys.path.append(os.getcwd())

from core.layer2_classification.classifier import CVDomainClassifier
from core.layer2_classification.domain_engine import DomainEngine
from core.layer2_classification.seniority_engine import SeniorityEngine
from core.layer3_matching.job_description_engine import JobDescriptionEngine
from core.layer3_matching.similarity import IntelligentMatcher
from core.layer3_matching.embedder import SemanticEmbedder

def test_full_matchmaking():
    # 1. Setup All Engines
    classifier = CVDomainClassifier()
    embedder = classifier.embedder
    domain_engine = DomainEngine(classifier)
    seniority_engine = SeniorityEngine(embedder)
    
    jd_engine = JobDescriptionEngine(domain_engine, seniority_engine)
    matcher = IntelligentMatcher(embedder, domain_engine)

    # 2. Load Yousef's CV Data (From the last successful run)
    with open("tests/yousef_output.json", "r", encoding="utf-8") as f:
        cv_data = json.load(f)

    # 3. Define a Senior Job Description
    senior_jd_text = """
    We are looking for a Senior Backend Developer.
    Requirements:
    - 5+ years of professional experience in Laravel.
    - Deep knowledge of PHP and MySQL.
    - Experience in Microservices and AWS.
    - Must have led a team of developers.
    """
    
    # 4. Step A: Parse the JD
    print("\n--- [Step 1] Parsing Senior JD ---")
    parsed_jd = jd_engine.parse_jd(senior_jd_text)
    print(f"Detected Level: {parsed_jd['seniority']}, Min Years: {parsed_jd['required_years_min']}")

    # 5. Step B: Calculate Match
    print("\n--- [Step 2] Calculating Match for Yousef (Intern) vs Senior JD ---")
    match_result = matcher.calculate_match(cv_data, parsed_jd)
    
    print("\n--- [Final Result] ---")
    print(json.dumps(match_result, indent=2))

if __name__ == "__main__":
    test_full_matchmaking()
