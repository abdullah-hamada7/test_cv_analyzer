import sys
import os
import json
from core.layer1_understanding.orchestrator import CVOrchestrator

# Mock the text extracted from the CV provided by the user
RAW_TEXT = """Abdullah Hamada AbdulAlim
Junior DevOps Engineer
chief.abdullah14@gmail.com — GitHub: abdullah-hamada7 — LinkedIn: abdullahhamada
Summary
Junior DevOps Engineer with hands-on experience in Linux administration, networking, AWS cloud, Terraform, CI/CD,
and scripting. Built and operated production web deployments using Nginx, Docker, and PostgreSQL on AWS. Familiar
with Kubernetes concepts, monitoring/logging stacks, and distributed-team collaboration through clear technical
documentation.
Education
Kafr El-Sheikh University | 2022–2026
B.Sc. in Computer Science, GPA: 3.78/4.0 — Honors: Top 3 Students
Professional Experience
Freelance DevOps/Cloud Engineer — Sezar Drive (Mostaql) | 2026–Present
Live Demo
• Owned end-to-end SDLC for a production web platform: architecture, MERN implementation, deployment, and
operations.
• Provisioned AWS with Terraform: VPC/subnets, security groups, EC2, Elastic IP, private RDS PostgreSQL, S3,
IAM, and SSM Parameter Store.
• Configured Nginx reverse proxy for HTTPS/TLS termination and routing; deployed services with Docker Compose.
• Implemented CI/CD with GitHub Actions + AWS OIDC for build/test/deploy and dependency/IaC/container
scanning.
• Operated PostgreSQL in production with troubleshooting, runbooks, and reliability/cost controls.
Freelance Deployment Engineer — Entity Medical Egypt (Mostaql) | 2026–Present
Live Demo
• Deployed a Python web app on Linux VPS infrastructure (Hostinger KVM) for production use.
• Configured OpenLiteSpeed + WSGI (lswsgi) for application serving and web server integration.
• Set up HTTPS using Let’s Encrypt (Certbot), SSL termination, and domain/DNS configuration.
• Managed static/media serving and resolved WSGI boot, CSRF/cookie, and reverse-proxy header issues
(SECURE PROXY SSL HEADER).
• Built a basic CI/CD flow: SSH to VPS, pull latest changes from Git, and reload services to apply updates safely.
DevOps Engineer Intern | 2025
• Built Jenkins and GitHub Actions pipelines and Ansible automation for repeatable provisioning and deployment.
• Worked with Docker and Kubernetes: Pods, Deployments, Services, ConfigMaps, Secrets, PVCs, and Ingress.
• Provisioned EKS with Terraform (public/private VPC, NAT, IAM/IRSA, remote state: S3 + DynamoDB lock).
• Delivered ProShop: Repository, with GitLab CI/CD, Helm/Kustomize, Prometheus/Grafana, Trivy, and Gitleaks.
Core Skills
• Linux & Networking: Linux admin, filesystem/permissions/services, TCP/IP, DNS, HTTP/HTTPS, SSL/TLS,
VPN, load balancers, firewalls
• Cloud Platforms: AWS (EKS, EC2, VPC, IAM, S3, RDS, CloudWatch, Route53)
• Web Deployment: Nginx, Apache, Docker, Kubernetes, Helm, Kustomize
• Infrastructure as Code: Terraform, Terragrunt, AWS CloudFormation
• CI/CD & GitOps: Jenkins, GitLab CI, GitHub Actions, ArgoCD; Git, GitHub, GitLab
• Scripting & Automation: Bash, Python, Ansible
• Security & Scanning: Trivy, Gitleaks, Semgrep, NJSScan, tfsec, RBAC, NetworkPolicies
• Monitoring & Logging: Prometheus, Grafana, AlertManager, CloudWatch
• Databases: PostgreSQL, MySQL, SQL Server, MongoDB, Redis
"""

def main():
    orchestrator = CVOrchestrator()
    # Run the NLP pipeline directly with the raw text
    result = orchestrator._run_nlp_pipeline(
        ordered_text=RAW_TEXT,
        raw_text_with_hints=RAW_TEXT,
        page_count=1,
        extraction_source="spatial",
        spatial_status="ok",
        spatial_word_count=len(RAW_TEXT.split()),
        filename="AbdullahHamada_cv.pdf"
    )
    
    print(json.dumps(result.model_dump(), indent=2, default=str))

if __name__ == "__main__":
    main()
