import csv
import json
import re
from typing import Any, Dict, Iterable, List

FIELDNAMES = ["Topic", "title", "content", "answer", "Tag"]
MAX_CHUNK_CHARS = 6000


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_topic_prefix(text: str) -> str:
    text = text.strip()
    if text.startswith("$$"):
        end = text.find("$$", 2)
        if end != -1:
            return text[end + 2 :].strip()
    return text


def _split_question_answer(text: str) -> Dict[str, str]:
    text = _strip_topic_prefix(text).replace("\\n", "\n").strip()
    if not text:
        return {"question": "", "answer": ""}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 2:
        return {"question": _clean_text(lines[0]), "answer": _clean_text("\n".join(lines[1:]))}

    inline = _clean_text(text)
    match = re.search(r"[？?]", inline)
    if match and match.end() < len(inline):
        return {
            "question": inline[: match.end()].strip(),
            "answer": inline[match.end() :].strip(),
        }

    return {"question": inline, "answer": ""}


def _split_lines(lines: Iterable[str], max_chars: int = MAX_CHUNK_CHARS) -> List[List[str]]:
    chunks: List[List[str]] = []
    current: List[str] = []
    current_len = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if current and current_len + len(line) > max_chars:
            chunks.append(current)
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line)

    if current:
        chunks.append(current)
    return chunks


def _extract_json_array(raw: str) -> List[Dict[str, Any]]:
    raw = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL | re.IGNORECASE)
    if fenced:
        raw = fenced.group(1).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(raw[start : end + 1])

    if isinstance(parsed, dict):
        for key in ("items", "data", "rows", "questions"):
            value = parsed.get(key)
            if isinstance(value, list):
                parsed = value
                break

    if not isinstance(parsed, list):
        raise ValueError("Qwen response is not a JSON array")

    return [item for item in parsed if isinstance(item, dict)]


def _normalize_row(item: Dict[str, Any], topic: str, fallback_text: str = "") -> Dict[str, str]:
    parsed = _split_question_answer(fallback_text)
    title = _clean_text(str(item.get("title") or item.get("题目标题") or ""))
    content = _clean_text(str(item.get("content") or item.get("题目内容") or ""))
    answer = _clean_text(str(item.get("answer") or item.get("参考答案") or ""))
    tag_value = item.get("Tag") or item.get("tag") or item.get("tags") or item.get("标签") or ""

    if isinstance(tag_value, list):
        tags = ",".join(_clean_text(str(tag)) for tag in tag_value if str(tag).strip())
    else:
        tags = _clean_text(str(tag_value)).replace("，", ",").replace("、", ",")

    if parsed["question"]:
        title = parsed["question"]
    elif not title:
        title = _clean_text(fallback_text)[:80] or topic

    content = title
    if parsed["answer"]:
        answer = parsed["answer"]

    return {
        "Topic": _clean_text(str(item.get("Topic") or item.get("topic") or item.get("主题") or topic)) or topic,
        "title": title,
        "content": content,
        "answer": answer,
        "Tag": tags,
    }


def _fallback_rows(lines: List[str], topic: str) -> List[Dict[str, str]]:
    rows = []
    for line in lines:
        parsed = _split_question_answer(line)
        if parsed["question"]:
            rows.append(
                {
                    "Topic": topic,
                    "title": parsed["question"],
                    "content": parsed["question"],
                    "answer": parsed["answer"],
                    "Tag": "",
                }
            )
    return rows


def _build_prompt(topic: str, lines: List[str]) -> str:
    numbered_text = "\n".join(f"{idx + 1}. {line}" for idx, line in enumerate(lines))
    return f"""你是知识图谱题库导入助手。请从下面上传文件内容中抽取题目数据，用于写入 Neo4j。

要求：
1. 只输出 JSON 数组，不要输出解释、Markdown 或多余文本。
2. 数组中每个对象必须包含字段：Topic、title、content、answer、Tag。
3. Topic 固定使用：{topic}
4. title 和 content 必须完全相同，都只放题目问题本身，不要放参考答案。
5. answer 只放参考答案。常见格式是“问题\\n答案”，第一行是问题，后续内容都是答案。
6. Tag 是逗号分隔的知识点标签，尽量抽取 1 到 5 个。
7. 如果一行就是一道题，按行抽取；不要把答案内容合并进 title 或 content。
8. 不要编造文件中没有依据的题目和答案。

文件内容：
{numbered_text}
"""


async def extract_graph_csv_with_qwen(topic: str, input_txt: str, output_csv: str) -> str:
    with open(input_txt, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    chunks = _split_lines(lines)
    rows: List[Dict[str, str]] = []

    for chunk in chunks:
        prompt = _build_prompt(topic, chunk)
        try:
            from app.services.AI.qwen_api import call_qwen_api

            raw = await call_qwen_api(prompt, max_tokens=4096, temperature=0.1)
            items = _extract_json_array(raw)
            if not items:
                rows.extend(_fallback_rows(chunk, topic))
                continue
            if len(items) != len(chunk):
                rows.extend(_fallback_rows(chunk, topic))
                continue
            rows.extend(_normalize_row(item, topic, chunk[idx]) for idx, item in enumerate(items))
        except Exception:
            rows.extend(_fallback_rows(chunk, topic))

    with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return output_csv
