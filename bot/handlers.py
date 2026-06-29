import re

from telegram import Update
from telegram.ext import ContextTypes

from bot.commands import command_help
from config.settings import get_settings
from core.briefing import generate_briefing
from core.extractor import extract_info
from core.material_manager import material_dashboard, record_delivery, report_need
from core.translator import translate_text
from models.database import (
    add_note,
    create_distribution_point,
    create_record,
    list_distribution_points,
    list_material_needs,
    list_records,
    update_status,
)
from models.schemas import (
    DeliveryRecordCreate,
    DistributionPointCreate,
    MaterialNeedCreate,
    MaterialType,
    MaterialUrgency,
    RecordStatus,
    RescueRecordCreate,
    priority_to_int,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else "未知"
    await update.message.reply_text(
        "你好，这里是 ArcaVida。转发西语或中文灾情文本即可生成求救记录。"
        f"\n当前 chat id：{chat_id}"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(command_help())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    raw_text = update.message.text
    translated = await translate_text(raw_text)
    extracted = await extract_info(translated.translated_text)
    record_id = create_record(
        RescueRecordCreate(
            raw_text=raw_text,
            detected_lang=translated.detected_lang,
            translated_text=translated.translated_text,
            location=extracted.location,
            needs=extracted.needs,
            trapped=extracted.trapped,
            priority=priority_to_int(extracted.priority),
            slang_alert=extracted.slang_alert,
            slang_hint=extracted.slang_meaning,
            source_chat_id=str(update.effective_chat.id),
        )
    )
    await update.message.reply_text(f"已创建求救记录：{record_id}")


async def briefing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    records = list_records(status=RecordStatus.pending)
    await update.message.reply_text(
        generate_briefing(records) if records else "当前没有待处理求救记录。"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    if context.args:
        point_name = context.args[0]
        point = find_point_by_name(point_name)
        if not point:
            await update.message.reply_text("未找到该安置点/发放点。")
            return
        needs = list_material_needs(point_id=point.id)
        if not needs:
            await update.message.reply_text(f"{point.name} 暂无物资需求记录。")
            return
        lines = [f"{point.name} 当前物资状态："]
        for need in needs:
            gap = max(0, need.quantity - need.current_stock)
            lines.append(
                f"{need.material_type}: 库存 {need.current_stock} {need.unit}，缺口 {gap} {need.unit}"
            )
        await update.message.reply_text("\n".join(lines))
        return
    pending = len(list_records(status=RecordStatus.pending))
    verified = len(list_records(status=RecordStatus.verified))
    dispatched = len(list_records(status=RecordStatus.dispatched))
    await update.message.reply_text(f"待处理：{pending}\n已核实：{verified}\n已派单：{dispatched}")


async def set_status(
    update: Update, context: ContextTypes.DEFAULT_TYPE, status_value: RecordStatus
) -> None:
    if not await require_operator(update):
        return
    if not context.args:
        await update.message.reply_text("请提供记录ID。")
        return
    ok = update_status(context.args[0], status_value)
    await update.message.reply_text("状态已更新。" if ok else "未找到记录。")


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_status(update, context, RecordStatus.verified)


async def dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_status(update, context, RecordStatus.dispatched)


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_status(update, context, RecordStatus.closed)


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    if len(context.args) < 2:
        await update.message.reply_text("用法：/note <id> <内容>")
        return
    record_id, note_text = context.args[0], " ".join(context.args[1:])
    ok = add_note(record_id, note_text)
    await update.message.reply_text("备注已更新。" if ok else "未找到记录。")


async def need(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    if len(context.args) < 3:
        await update.message.reply_text("用法：/need <点位> <物资> <数量单位>")
        return
    point = find_or_create_point(context.args[0])
    quantity, unit = parse_quantity(context.args[2])
    material_type = parse_material_type(context.args[1])
    need_id = report_need(
        MaterialNeedCreate(
            point_id=point.id,
            material_type=material_type,
            quantity=quantity,
            unit=unit,
            urgency=MaterialUrgency.high,
            reported_channel="telegram",
        )
    )
    await update.message.reply_text(f"已记录物资需求：{need_id}")


async def deliver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    if len(context.args) < 3:
        await update.message.reply_text("用法：/deliver <点位> <物资> <数量单位>")
        return
    point = find_point_by_name(context.args[0])
    if not point:
        await update.message.reply_text("未找到该安置点/发放点。")
        return
    quantity, unit = parse_quantity(context.args[2])
    delivery_id = record_delivery(
        DeliveryRecordCreate(
            point_id=point.id,
            material_type=parse_material_type(context.args[1]),
            quantity=quantity,
            unit=unit,
            delivered_by="telegram",
        )
    )
    await update.message.reply_text(f"已记录物资送达：{delivery_id}")


async def shortage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_operator(update):
        return
    requested_type = parse_material_type(context.args[0]) if context.args else None
    items = material_dashboard()["needs"]
    if requested_type:
        items = [item for item in items if item["need"]["material_type"] == requested_type.value]
    if not items:
        await update.message.reply_text("暂无物资缺口记录。")
        return
    lines = ["物资缺口最高的点位："]
    for item in items[:5]:
        need_data = item["need"]
        gap = max(0, need_data["quantity"] - need_data["current_stock"])
        lines.append(
            f"{item['point']['name']} {need_data['material_type']} 缺 {gap} {need_data['unit']}，缺货指数 {item['shortage_index']}"
        )
    await update.message.reply_text("\n".join(lines))


async def require_operator(update: Update) -> bool:
    settings = get_settings()
    allowed_chat_ids = settings.operator_chat_id_set()
    chat_id = str(update.effective_chat.id) if update.effective_chat else ""
    if allowed_chat_ids and chat_id in allowed_chat_ids:
        return True
    if not allowed_chat_ids and settings.environment.lower() != "production":
        return True
    await update.message.reply_text("此命令仅限授权协调员使用。")
    return False


def find_point_by_name(name: str):
    normalized = name.strip().lower()
    for point in list_distribution_points():
        if point.name.lower() == normalized:
            return point
    return None


def find_or_create_point(name: str):
    point = find_point_by_name(name)
    if point:
        return point
    point_id = create_distribution_point(DistributionPointCreate(name=name.strip()))
    return find_point_by_name(name) or next(
        point for point in list_distribution_points() if point.id == point_id
    )


def parse_material_type(value: str) -> MaterialType:
    normalized = value.strip().lower()
    mapping = {
        "水": MaterialType.water,
        "agua": MaterialType.water,
        "water": MaterialType.water,
        "食物": MaterialType.food,
        "食品": MaterialType.food,
        "comida": MaterialType.food,
        "food": MaterialType.food,
        "卫生用品": MaterialType.hygiene_kit,
        "hygiene": MaterialType.hygiene_kit,
        "药": MaterialType.medicine,
        "药品": MaterialType.medicine,
        "medicine": MaterialType.medicine,
        "帐篷": MaterialType.tent,
        "tent": MaterialType.tent,
    }
    return mapping.get(normalized, MaterialType.other)


def parse_quantity(value: str) -> tuple[int, str]:
    match = re.match(r"^(\d+)(.*)$", value.strip())
    if not match:
        return 0, "units"
    unit = match.group(2).strip() or "units"
    return int(match.group(1)), unit
