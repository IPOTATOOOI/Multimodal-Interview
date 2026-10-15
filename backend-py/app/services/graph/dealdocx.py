import json
from pathlib import Path
from docx import Document

def convert_docx_to_jsonl_with_prefix(input_path: str, output_path: str, prefix: str = "$$移动通信$$"):
    """
    将DOCX文件转换为带前缀的JSONL格式文件，每段落作为一条题目
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    doc = Document(input_file)
    record_id = 1
    with output_file.open('w', encoding='utf-8', newline='') as fout:
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            new_text = f"{prefix}{text}"
            obj = {"id": record_id, "text": new_text}
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            record_id += 1

def process_docx_to_txt(input_path: str, output_jsonl: str, output_txt: str, prefix: str = "$$移动通信$$"):
    convert_docx_to_jsonl_with_prefix(input_path, output_jsonl, prefix)
    from app.services.graph.dealtxt import extract_text_to_jsonl
    extract_text_to_jsonl(output_jsonl, output_txt)
