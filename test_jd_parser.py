import sys
import os
# Ensure we can import from core
sys.path.append(os.getcwd())

from core.layer2_classification.classifier import CVDomainClassifier
from core.layer2_classification.domain_engine import DomainEngine
from core.layer2_classification.seniority_engine import SeniorityEngine
from core.layer3_matching.job_description_engine import JobDescriptionEngine
import json

def test_parser():
    # Setup engines
    classifier = CVDomainClassifier()
    domain_engine = DomainEngine(classifier)
    seniority_engine = SeniorityEngine(classifier.embedder)
    jd_engine = JobDescriptionEngine(domain_engine, seniority_engine)

    # Sample raw JD text
    sample_jd = """
    We are looking for a Senior Backend Developer to join our team.
    
    Requirements:
    - 5+ years of experience in PHP and Laravel.
    - Strong knowledge of MySQL and Database Design.
    - Experience with RESTful APIs and Microservices.
    - Solid understanding of SOLID principles.
    
    Nice to have:
    - Experience with Docker and Kubernetes.
    - Knowledge of AWS or Azure.
    - Unit testing experience with PHPUnit.
    
    Responsibilities:
    - Building scalable backend services.
    - Mentoring junior developers.
    """

    print("--- Parsing Sample JD ---")
    result = jd_engine.parse_jd(sample_jd)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_parser()
