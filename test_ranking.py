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
from core.layer3_matching.ranking_orchestrator import RankingOrchestrator

def test_ranking_pipeline():
    # 1. Setup All Engines
    classifier = CVDomainClassifier()
    embedder = classifier.embedder
    domain_engine = DomainEngine(classifier)
    seniority_engine = SeniorityEngine(embedder)
    
    jd_engine = JobDescriptionEngine(domain_engine, seniority_engine)
    matcher = IntelligentMatcher(embedder, domain_engine)
    orchestrator = RankingOrchestrator(matcher, jd_engine)

    # 2. Load Multiple CVs
    cvs = []
    for filename in ["tests/yousef_output.json", "tests/ahmed_output.json"]:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                cvs.append(json.load(f))

    # 3. Define a Junior Backend/Fullstack Job Description
    # This role should fit Yousef well but also Ahmed (who has mobile skills but also some backend)
    junior_jd = """
    Junior Laravel Developer.
    Requirements:
    - 0-2 years of experience.
    - Strong skills in PHP and Laravel.
    - Understanding of MySQL and APIs.
    - Knowledge of Flutter is a bonus.
    """
    
    print("\n--- [Ranking Pipeline] Testing 1 JD vs 2 Candidates ---")
    results = orchestrator.rank_candidates(cvs, junior_jd)
    
    print("\n--- [Final Ranking] ---")
    for rank, cand in enumerate(results["rankings"], 1):
        print(f"{rank}. {cand['candidate_name']} - Score: {cand['match_score']}% ({cand['verdict']})")
    
    # Save the full result for verification
    with open("tests/ranking_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    test_ranking_pipeline()
