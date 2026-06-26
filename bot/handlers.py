from telegram import Update
from telegram.ext import ContextTypes

from bot.commands import command_help
from config.settings import get_settings
from core.briefing import generate_briefing
from core.extractor import extract_info
from core.translator import translate_text
from models.database import (
    add_note,
    create_record,
    list_records,
    update_status,
)
from models.schemas import RecordStatus, RescueRecordCreate, priority_to_int


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
