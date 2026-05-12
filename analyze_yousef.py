import json
import os
from main import process_file

file_path = r"tests\Yousef_Altohamy_CV.pdf"
output_path = r"tests\yousef_output.json"

if os.path.exists(file_path):
    print(f"Processing {file_path}...")
    result = process_file(file_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Done! Result saved to {output_path}")
else:
    print(f"File not found: {file_path}")
