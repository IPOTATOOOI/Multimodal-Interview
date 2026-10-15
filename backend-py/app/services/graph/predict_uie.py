import argparse
import csv
import sys
import os
import re
from typing import List, Dict, Tuple
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import paddle
from paddlenlp.transformers import AutoModelForCausalLM, AutoTokenizer
from paddlenlp.generation import GenerationConfig
from paddlenlp.trl import llm_utils


def read_jsonl(path: str) -> List[dict]:
    """读取JSONL文件"""
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
    return examples


def extract_question_type(src: str) -> str:
    """从src中提取问题类型"""
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '**问题开始**':
            if i + 1 < len(lines):
                return lines[i + 1].strip()
    return ""


def extract_text_content(src: str) -> str:
    """从src中提取文本内容"""
    match = re.search(r"\*\*句子开始\*\*\n(.*?)\n\*\*句子结束\*\*", src, re.DOTALL)
    return match.group(1).strip() if match else ""


def create_prompt(text_content: str, question_type: str) -> str:
    """创建prompt"""
    template = """你是一个阅读理解专家，请提取所给句子与问题，提取实体。请注意，如果存在实体，则一定在原句中逐字出现，请输出对应实体的原文，不要进行额外修改；如果无法提取，请输出"无相应实体"。
**句子开始**
{}
**句子结束**
**问题开始**
{}
**问题结束**
**回答开始**
"""
    return template.format(text_content, question_type)


def extract_answer(text: str) -> str:
    """提取答案"""
    # Robustly cut off at the answer end marker, tolerate optional spaces/newlines
    if "**回答结束**" in text:
        text = text.split("**回答结束**", 1)[0]
    return text.strip()


def batch_iter(items: List, batch_size: int):
    """批量迭代器"""
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def predict_batch(model, tokenizer, generation_config, batch_prompts: List[str], args) -> List[str]:
    """批量预测"""
    # Apply chat template then tokenize
    inputs_text = [tokenizer.apply_chat_template(prompt, tokenize=False) for prompt in batch_prompts]
    input_features = tokenizer(
        inputs_text,
        max_length=args.src_length,
        return_position_ids=False,
        truncation=True,
        truncation_side="left",
        padding=True,
        return_tensors="pd",
        add_special_tokens=False,
    )

    with paddle.no_grad():
        outputs = model.generate(
            **input_features,
            max_new_tokens=max(1, args.max_length - args.src_length),
            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=llm_utils.get_eos_token_id(tokenizer, generation_config),
            pad_token_id=tokenizer.pad_token_id,
            decode_strategy="greedy_search",
            temperature=1.0,
            top_k=1,
            top_p=1.0,
            repetition_penalty=1.0,
        )

    texts = tokenizer.batch_decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return texts


def process_single_text(model, tokenizer, generation_config, text_content: str, args) -> Dict[str, str]:
    """处理单个文本，获取所有类型的预测结果"""
    question_types = ["Topic", "title", "content", "answer", "Tag"]
    results = {}
    
    # 为每种问题类型创建prompt
    prompts = [create_prompt(text_content, q_type) for q_type in question_types]
    
    # 批量预测
    predictions = predict_batch(model, tokenizer, generation_config, prompts, args)
    
    # 处理预测结果
    for i, q_type in enumerate(question_types):
        answer = extract_answer(predictions[i])
        results[q_type] = answer if answer != "无相应实体" else ""
        
    return results

def predict_uie(
    model_name_or_path: str,
    data_file: str,
    output_file: str,
    src_length: int = 1024,
    max_length: int = 2048,
    batch_size: int = 8,
    precision: str = "float16",
    use_flash_attention: bool = False
) -> str:
    """
    以方法形式调用，处理指定txt文件，输出csv结果
    返回csv文件路径
    """
    assert os.path.exists(data_file), f"data_file not found: {data_file}"
    dtype_map = {"float16": "float16", "bfloat16": "bfloat16", "float32": "float32"}
    dtype = dtype_map.get(precision, "float16")
    # Load model/tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        dtype=dtype,
        use_flash_attention=use_flash_attention,
    )
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, padding_side="left")
    generation_config = GenerationConfig.from_pretrained(model_name_or_path)
    # Read data
    with open(data_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    fieldnames = ["Topic", "title", "content", "answer", "Tag"]
    with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            text_content = line
            result = process_single_text(model, tokenizer, generation_config, text_content, argparse.Namespace(
                src_length=src_length,
                max_length=max_length,
                batch_size=batch_size,
                precision=precision,
                use_flash_attention=use_flash_attention
            ))
            writer.writerow(result)
    return output_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str, default="./ie_ckpts", help="Path to finetuned checkpoints")
    parser.add_argument("--data_file", type=str, default="../ComputerNetwork_text_only.txt", help="Path to input TXT file (one complete data per line)")
    parser.add_argument("--output_file", type=str, default="./uie_predictions.csv", help="Where to save predictions in CSV format")
    parser.add_argument("--src_length", type=int, default=1024)
    parser.add_argument("--max_length", type=int, default=2048)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--precision", type=str, choices=["float16", "bfloat16", "float32"], default="float16")
    parser.add_argument("--use_flash_attention", action="store_true", help="Enable flash attention if available")
    args = parser.parse_args()
    predict_uie(
        model_name_or_path=args.model_name_or_path,
        data_file=args.data_file,
        output_file=args.output_file,
        src_length=args.src_length,
        max_length=args.max_length,
        batch_size=args.batch_size,
        precision=args.precision,
        use_flash_attention=args.use_flash_attention
    )


if __name__ == "__main__":
    main()