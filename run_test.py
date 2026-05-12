import json
from main import process_file

file_path = r"tests\Flutter Developer_CV_Ahmed_Khames .pdf.pdf"
result = process_file(file_path)
with open("test_output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
