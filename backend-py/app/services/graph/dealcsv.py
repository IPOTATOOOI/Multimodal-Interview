import csv
import json
from pathlib import Path

def convert_csv_to_jsonl_with_prefix(input_path: str, output_path: str, prefix: str = "$$移动通信$$"):
    """
    将CSV文件转换为带前缀的JSONL格式文件，每行（第一列）作为一条题目
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    # 自动尝试 utf-8 和 gbk 编码
    try:
        fin = input_file.open('r', encoding='utf-8')
        reader = csv.reader(fin)
        test_row = next(reader)
        fin.seek(0)
    except Exception:
        fin = input_file.open('r', encoding='gbk')
        reader = csv.reader(fin)
    with fin, output_file.open('w', encoding='utf-8', newline='') as fout:
        record_id = 1
        for row in reader:
            if not row or not row[0].strip():
                continue
            new_text = f"{prefix}{row[0].strip()}"
            obj = {"id": record_id, "text": new_text}
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            record_id += 1

def process_csv_to_txt(input_path: str, output_jsonl: str, output_txt: str, prefix: str = "$$移动通信$$"):
    convert_csv_to_jsonl_with_prefix(input_path, output_jsonl, prefix)
    from app.services.graph.dealtxt import extract_text_to_jsonl
    extract_text_to_jsonl(output_jsonl, output_txt)
