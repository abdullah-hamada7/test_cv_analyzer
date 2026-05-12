import os
import json
import logging
from main import process_file

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)

def test_ahmed_cv():
    # Use the correct path found
    cv_path = r"tests\Flutter Developer_CV_Ahmed_Khames .pdf.pdf"
    
    if not os.path.exists(cv_path):
        print(f"Error: File {cv_path} not found!")
        return

    print(f"Starting analysis for: {cv_path}")
    result = process_file(cv_path)
    
    output_file = "tests/ahmed_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Done! Result saved to {output_file}")

if __name__ == "__main__":
    test_ahmed_cv()
