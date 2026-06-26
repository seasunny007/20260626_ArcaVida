COMMANDS = {
    "start": "欢迎消息，显示使用指引",
    "help": "显示所有命令列表",
    "briefing": "生成当前所有待处理求救的简报",
    "verify": "将指定ID状态改为已核实",
    "dispatch": "将指定ID状态改为已派单",
    "close": "将指定ID状态改为已关闭",
    "note": "为记录添加备注",
    "status": "显示当前待处理数量统计",
}


def command_help() -> str:
    return "\n".join(f"/{name} - {description}" for name, description in COMMANDS.items())
