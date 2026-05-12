import unittest
from core.layer1_understanding.orchestrator import CVOrchestrator
from core.layer1_understanding.contact_extractor import extract_contacts
from core.layer1_understanding.skill_scanner import SkillScanner

class TestExtractionRegression(unittest.TestCase):
    
    def setUp(self):
        # We don't need a full orchestrator for simple regex tests, 
        # but for end-to-end we might.
        self.scanner = SkillScanner()
        
    def test_skill_scanner_recall(self):
        text = "Skills: Linux, AWS, Docker, Kubernetes, Terraform, Jenkins, Python, PostgreSQL"
        skills = self.scanner.scan_text(text)
        
        self.assertIn("Linux", skills)
        self.assertIn("AWS", skills)
        self.assertIn("Docker", skills)
        self.assertIn("Kubernetes", skills)
        self.assertIn("Terraform", skills)
        self.assertIn("Python", skills)
        self.assertIn("PostgreSQL", skills)
        
    def test_location_validation(self):
        # Problematic text from user CV
        text = "chief.abdullah14@gmail.com — GitHub: abdullah-hamada7 — LinkedIn: abdullahhamada\nAWS cloud, Terraform, CI/CD"
        contacts = extract_contacts(text)
        
        # Location should NOT be "AWS cloud, Terraform"
        loc = contacts.get("location")
        if loc:
            self.assertNotIn("AWS", loc)
            self.assertNotIn("Terraform", loc)
            
    def test_linkedin_capture(self):
        text = "LinkedIn: abdullahhamada — GitHub: abdullah-hamada7"
        contacts = extract_contacts(text)
        
        self.assertEqual(contacts.get("linkedin_url"), "https://www.linkedin.com/in/abdullahhamada")
        self.assertNotEqual(contacts.get("linkedin_url"), "https://www.linkedin.com/in/DNS")

if __name__ == "__main__":
    unittest.main()
