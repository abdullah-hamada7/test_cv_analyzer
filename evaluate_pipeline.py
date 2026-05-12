import json
import os

def evaluate_pipeline_performance():
    results_path = "tests/ranking_results.json"
    if not os.path.exists(results_path):
        print("Error: No ranking results found. Run test_ranking.py first.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "="*50)
    print("       AI PIPELINE EVALUATION REPORT")
    print("="*50)
    
    job_info = data["job_info"]
    print(f"Target Role: {job_info['title']}")
    print(f"Candidates Analyzed: {data['total_candidates']}")
    print("-" * 50)

    for i, cand in enumerate(data["rankings"], 1):
        print(f"Rank {i}: {cand['candidate_name']}")
        print(f"  > Final Score: {cand['match_score']}%")
        print(f"  > AI Verdict: {cand['verdict']}")
        
        details = cand["full_match_details"]
        print(f"  > Strengths: {', '.join(details['fit_analysis']['strengths']) if details['fit_analysis']['strengths'] else 'None'}")
        
        missing = details["missing_mandatory_skills"]
        if missing:
            print(f"  > Missing Mandatory: {', '.join(missing)}")
            
        penalty = details["breakdown"]["penalty_deduction"]
        if penalty > 0:
            print(f"  > Logic Penalties: -{penalty}%")
            
        bonus = details["breakdown"]["bonus_boost"]
        if bonus > 0:
            print(f"  > Bonus Boost: +{bonus}%")
            
        print("-" * 30)

    print("\nCONCLUSION:")
    if data["shortlisted_count"] > 0:
        print(f"[OK] Pipeline successfully identified {data['shortlisted_count']} qualified candidates.")
    else:
        print("[WARN] No candidates met the minimum pass threshold (50%).")
        print("Reason: Most candidates had seniority mismatches or missing core skills.")
    print("="*50 + "\n")

if __name__ == "__main__":
    evaluate_pipeline_performance()
