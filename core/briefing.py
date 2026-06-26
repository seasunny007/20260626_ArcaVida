from collections import Counter

from models.schemas import RescueRecord

# LLM 简报提示词，生成草稿而非最终事实结论 / LLM briefing prompt for drafts, not final factual conclusions.
BRIEFING_PROMPT = """
你是一名救援简报撰写员。根据以下求救记录生成中文简报。

记录列表：{records_json}

要求：
1. 按优先级从高到低排序（高→中→低）
2. 每条格式：[优先级] 地点 | 需求 | 被困情况 | 状态
3. 末尾汇总：总求救数、高优先级数、被困人数
4. 如某区域出现≥3条，标注“⚠️ 聚焦区域：XX地点”
5. 如检测到暗语的记录，附加“⚠️ 暗语提醒”
""".strip()


PRIORITY_LABELS = {3: "高", 2: "中", 1: "低"}


def area_key(location: str) -> str:
    return location.split()[0].split("，")[0].split(",")[0] if location else "待核实"


def generate_briefing(records: list[RescueRecord]) -> str:
    ordered = sorted(records, key=lambda record: (-record.priority, record.created_at))
    lines = ["ArcaVida 求救简报"]

    for record in ordered:
        priority = PRIORITY_LABELS.get(record.priority, "低")
        needs = "、".join(record.needs) if record.needs else "待核实"
        trapped = "被困" if record.trapped else "未确认被困"
        slang = " ⚠️ 暗语提醒" if record.slang_alert else ""
        lines.append(
            f"[{priority}] {record.location or '待核实'} | {needs} | {trapped} | {record.status}{slang}"
        )

    high_count = sum(1 for record in records if record.priority == 3)
    trapped_count = sum(1 for record in records if record.trapped)
    lines.append(f"汇总：总求救数 {len(records)}，高优先级 {high_count}，被困 {trapped_count}")

    for area, count in Counter(area_key(record.location) for record in records).items():
        if count >= 3:
            lines.append(f"⚠️ 聚焦区域：{area}")

    return "\n".join(lines)
