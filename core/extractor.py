import json
import re

from config.settings import get_settings
from core.slang_matcher import format_slang_hint, match_slang
from models.schemas import ExtractedInfo

# LLM 提取提示词，输出仍需人工复核 / LLM extraction prompt; output still needs human review.
EXTRACT_PROMPT = """
你是一名灾害应急信息分析师。从以下文本中提取关键信息，严格输出JSON。

文本：{raw_text}

必须输出以下字段，不要有多余内容：
{{
  "location": "地点描述（尽可能精确，参照物保留）",
  "needs": ["物资1", "物资2"],
  "trapped": true,
  "priority": "low/medium/high",
  "slang_alert": true,
  "slang_meaning": "如检测到暗语在此解释，否则为null"
}}

优先级判断：
- high: 包含'被困'、'重伤'、'倒塌'、'atrapado'、'grave'
- medium: 包含'医疗'、'食物'、'agua'、'comida'
- low: 其他
""".strip()


# 本地回退关键词表 / Local fallback keyword table.
NEED_KEYWORDS = {
    "水": ["水", "agua"],
    "食物": ["食物", "食品", "comida", "pan"],
    "医疗": ["医疗", "药", "救护", "medico", "médico", "hospital"],
    "撤离": ["撤离", "转移", "evacuar", "evacuacion", "evacuación"],
}


def heuristic_extract(text: str) -> ExtractedInfo:
    lowered = text.lower()
    needs = [
        label for label, words in NEED_KEYWORDS.items() if any(word in lowered for word in words)
    ]
    trapped = any(word in lowered for word in ["被困", "困住", "atrapado", "atrapada"])
    high = any(
        word in lowered for word in ["被困", "重伤", "倒塌", "atrapado", "atrapada", "grave"]
    )
    medium = any(word in lowered for word in ["医疗", "食物", "agua", "comida", "médico", "medico"])
    location_match = re.search(
        r"(?:在|地点[:：]?|ubicaci[oó]n[:：]?|en)\s*([^，。,.\n]+)", text, re.IGNORECASE
    )
    slang_matches = match_slang(text)

    return ExtractedInfo(
        location=location_match.group(1).strip() if location_match else "待核实",
        needs=needs,
        trapped=trapped,
        priority="high" if high else "medium" if medium else "low",
        slang_alert=bool(slang_matches),
        slang_meaning=format_slang_hint(slang_matches),
    )


async def extract_info(text: str, use_llm: bool = True) -> ExtractedInfo:
    settings = get_settings()
    if not use_llm or not settings.openai_api_key:
        return heuristic_extract(text)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": EXTRACT_PROMPT.format(raw_text=text)}],
            temperature=0.1,
            max_tokens=220,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return ExtractedInfo.model_validate(json.loads(content))
    except Exception:
        return heuristic_extract(text)
