import json
import sys
from pathlib import Path


def extract_text_to_jsonl(input_file, output_file):
    """
    从JSONL文件中提取text字段，创建新的只包含文本内容的文件

    Args:
        input_file (str): 输入的JSONL文件路径
        output_file (str): 输出的文本文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            # 跳过空行
            if not line:
                continue

            # 跳过可能的文件名行
            if line.startswith("ComputerNetwork.jsonl"):
                continue

            try:
                # 解析每一行JSON数据
                data = json.loads(line)

                # 只提取text字段内容并写入文件
                text_content = data.get("text", "")
                if text_content:
                    outfile.write(text_content + '\n')  # 用一个换行符分隔不同的文本块

            except json.JSONDecodeError as e:
                print(f"警告: 第{line_num}行JSON解析失败，已跳过: {e}")
                continue


def convert_to_jsonl_with_prefix(input_path: str, output_path: str, prefix: str = "$$移动通信$$",
                                 skip_empty_lines: bool = True):
    """
    将文本文件转换为带前缀的JSONL格式文件

    Args:
        input_path (str): 输入的文本文件路径
        output_path (str): 输出的JSONL文件路径
        prefix (str): 添加到每行前的前缀，默认为"$$移动通信$$"
        skip_empty_lines (bool): 是否跳过空行，默认为True
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"错误：找不到输入文件: {input_file}", file=sys.stderr)
        return

    try:
        with input_file.open('r', encoding='utf-8') as fin, \
                output_file.open('w', encoding='utf-8', newline='') as fout:

            record_id = 1
            for raw_line in fin:
                line = raw_line.rstrip('\r\n')
                if skip_empty_lines and line.strip() == "":
                    continue

                new_text = f"{prefix}{line}"

                obj = {
                    "id": record_id,
                    "text": new_text
                }
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                record_id += 1

        print(f"已成功生成带前缀的 JSONL 文件：{output_file}")

    except Exception as e:
        print("发生错误：", e, file=sys.stderr)


# 示例1: 将文本文件转换为JSONL格式
# convert_to_jsonl_with_prefix(r"MobileCommunication.txt", r"MobileCommunication.jsonl")

# 示例2: 从JSONL文件提取纯文本
# extract_text_to_jsonl(r"D:\桌面\questionBank\ComputerNetwork.jsonl", r"D:\桌面\questionBank\ComputerNetwork_text_only.txt")
