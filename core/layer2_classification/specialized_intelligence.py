import logging
import json
import os
from typing import List, Dict, Set, Any, Optional

logger = logging.getLogger(__name__)

class SpecializedIntelligenceEngine:
    """
    Engine for generating deep, sector-specific insights and strengths.
    Loads rules from taxonomy.json to avoid hardcoding.
    """

    def __init__(self):
        self._rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Loads specialized rules from taxonomy.json."""
        try:
            base_path = os.path.dirname(__file__)
            taxonomy_path = os.path.join(base_path, "data", "taxonomy.json")
            if os.path.exists(taxonomy_path):
                with open(taxonomy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("specialized_rules", {})
        except Exception as e:
            logger.error("Failed to load specialized rules from taxonomy: %s", e)
        return {}

    def generate_strengths(self, cv_data: Dict[str, Any]) -> List[str]:
        """
        Analyzes the CV data and returns a list of identified strengths/insights.
        Uses configuration-driven rules based on the primary domain.
        """
        strengths = []
        
        # 1. Extract necessary data
        skills_items = cv_data.get("skills", {}).get("items", [])
        skills_names = {s.get("name", "").lower() for s in skills_items}
        
        analysis = cv_data.get("analysis", {})
        primary_domain = analysis.get("primary_domain", "Technology & Software")
        experience_years = analysis.get("metadata", {}).get("experience", {}).get("total_experience_years", 0)
        
        # 2. Get rules for the current domain
        domain_rules = self._rules.get(primary_domain, {})
        if not domain_rules and primary_domain != "Technology & Software":
            # Fallback to Technology if primary domain not found (for safety)
            domain_rules = self._rules.get("Technology & Software", {})

        # 3. Check for Stack-Specific Expertise
        stacks = domain_rules.get("stacks", {})
        for stack_name, keywords in stacks.items():
            keywords_set = set(k.lower() for k in keywords)
            matched = skills_names.intersection(keywords_set)
            if len(matched) >= 2:
                if "Backend" in stack_name:
                    strengths.append(f"Specialized {stack_name} developer with proficiency in {', '.join(list(matched)[:3])}.")
                elif "Frontend" in stack_name:
                    strengths.append(f"Expertise in {stack_name} ecosystem, including {', '.join(list(matched)[:3])}.")
                elif "Mobile" in stack_name:
                    strengths.append(f"Mobile development focus in {stack_name} ({', '.join(list(matched)[:3])}).")
                else:
                    strengths.append(f"Strong foundation in {stack_name} ({', '.join(list(matched)[:3])}).")

        # 4. Sector-Specific "Advanced" Logic (from config)
        advanced_rules = domain_rules.get("advanced", [])
        for rule in advanced_rules:
            if_keywords = set(k.lower() for k in rule.get("if", []))
            if if_keywords.issubset(skills_names):
                strengths.append(rule.get("then", ""))

        # 5. Cross-Functional Logic (Still partially hardcoded but more generic)
        is_backend = any("Backend" in s for s in strengths)
        is_frontend = any("Frontend" in s for s in strengths)
        if is_backend and is_frontend:
            strengths.append("Versatile Full Stack Profile: Demonstrated competency across both backend and frontend ecosystems.")

        # Seniority-based strengths
        if experience_years >= 8:
            strengths.append(f"Seasoned professional with {experience_years} years of industry experience.")

        return list(dict.fromkeys([s for s in strengths if s])) # Deduplicate and remove empty
