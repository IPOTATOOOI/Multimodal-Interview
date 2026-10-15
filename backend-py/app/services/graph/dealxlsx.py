import json
from pathlib import Path
import openpyxl

def convert_xlsx_to_jsonl_with_prefix(input_path: str, output_path: str, prefix: str = "$$移动通信$$"):
    """
    将XLSX文件转换为带前缀的JSONL格式文件，每行（第一列）作为一条题目
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active
    record_id = 1
    with output_file.open('w', encoding='utf-8', newline='') as fout:
        for row in ws.iter_rows(min_row=1, values_only=True):
            if not row or not row[0] or not str(row[0]).strip():
                continue
            new_text = f"{prefix}{str(row[0]).strip()}"
            obj = {"id": record_id, "text": new_text}
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            record_id += 1

def process_xlsx_to_txt(input_path: str, output_jsonl: str, output_txt: str, prefix: str = "$$移动通信$$"):
    convert_xlsx_to_jsonl_with_prefix(input_path, output_jsonl, prefix)
    from app.services.graph.dealtxt import extract_text_to_jsonl
    extract_text_to_jsonl(output_jsonl, output_txt)
