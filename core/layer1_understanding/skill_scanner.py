import re
import logging
from typing import List, Set, Dict

logger = logging.getLogger(__name__)

# Core Categories for Technical Skill Scanning
# This dictionary contains common technical keywords grouped by category.
# These will be used for deterministic regex-based extraction.
TECH_DICTIONARY: Dict[str, List[str]] = {
    "Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C\\+\\+", "C\\#", "Go", "Golang", 
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Bash", "Shell", "PowerShell",
        "HTML", "CSS", "SQL", "NoSQL", "GraphQL", "Perl", "R", "Dart"
    ],
    "Cloud & Infrastructure": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "DigitalOcean", 
        "Heroku", "Cloudflare", "Terraform", "Terragrunt", "CloudFormation", "Ansible", 
        "Pulumi", "CDK", "VPC", "EC2", "S3", "RDS", "Lambda", "IAM", "Route53", 
        "CloudWatch", "Azure DevOps", "Serverless"
    ],
    "Containers & Orchestration": [
        "Docker", "Kubernetes", "K8s", "EKS", "AKS", "GKE", "Helm", "Kustomize", 
        "ArgoCD", "Docker Compose", "Nomad", "OpenShift", "LXC"
    ],
    "CI/CD & Tools": [
        "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "TravisCI", "Bitbucket Pipelines",
        "Git", "GitHub", "GitLab", "Bitbucket", "Nginx", "Apache", "HAProxy", "SonarQube"
    ],
    "Monitoring & Logging": [
        "Prometheus", "Grafana", "ELK Stack", "Elasticsearch", "Logstash", "Kibana", 
        "Splunk", "Datadog", "New Relic", "Sentry", "AlertManager", "Zabbix", "Nagios"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "Postgres", "SQL Server", "MongoDB", "Redis", "Cassandra", 
        "DynamoDB", "Oracle", "SQLite", "Elasticsearch", "Firebase", "Neo4j"
    ],
    "DevSecOps": [
        "Trivy", "Gitleaks", "Semgrep", "tfsec", "Checkov", "NJSScan", "Vault", "OWASP",
        "Penetration Testing", "Security Auditing", "RBAC", "NetworkPolicies", "SSL/TLS"
    ],
    "Operating Systems": [
        "Linux", "Ubuntu", "Debian", "CentOS", "RedHat", "RHEL", "Alpine", "Windows Server", "macOS"
    ],
    "Networking": [
        "TCP/IP", "DNS", "HTTP", "HTTPS", "SSL", "TLS", "VPN", "Load Balancing", "Firewalls", "BGP", "OSPF"
    ]
}

class SkillScanner:
    """
    Deterministic keyword-based skill scanner.
    Ensures 100% recall for common technical terms that NER might miss.
    """
    
    def __init__(self):
        self._patterns = {}
        self._all_keywords = []
        
        # Compile case-insensitive patterns for each category
        for category, keywords in TECH_DICTIONARY.items():
            # Sort by length descending to match "GitLab CI" before "Git"
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            # Use word boundaries \b except for tokens ending in special chars like C++
            pattern_str = r'|'.join([rf'\b{re.escape(k)}\b' if k[-1].isalnum() else rf'\b{re.escape(k)}' for k in sorted_keywords])
            self._patterns[category] = re.compile(pattern_str, re.IGNORECASE)
            self._all_keywords.extend(keywords)

    def scan_text(self, text: str) -> List[str]:
        """
        Scan text for all known technical keywords.
        Returns a deduplicated list of found skills (original casing from dictionary).
        """
        if not text:
            return []
            
        found_skills: Set[str] = set()
        
        for category, pattern in self._patterns.items():
            matches = pattern.findall(text)
            for m in matches:
                # We need to find the original casing from the dictionary for consistency
                # but findall might return a lowercased match if the text has it.
                # Heuristic: find the keyword in our list that matches case-insensitively
                for kw in TECH_DICTIONARY[category]:
                    if kw.lower() == m.lower():
                        found_skills.add(kw)
                        break
        
        return sorted(list(found_skills))

    def get_skills_by_category(self, text: str) -> Dict[str, List[str]]:
        """
        Scan text and group results by category.
        """
        results = {}
        for category, pattern in self._patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Deduplicate and fix casing
                category_skills = set()
                for m in matches:
                    for kw in TECH_DICTIONARY[category]:
                        if kw.lower() == m.lower():
                            category_skills.add(kw)
                            break
                results[category] = sorted(list(category_skills))
        return results
