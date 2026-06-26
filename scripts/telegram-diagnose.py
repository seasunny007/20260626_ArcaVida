#!/usr/bin/env python

import argparse
import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from telegram import Bot

from config.settings import get_settings


async def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose the optional Telegram adapter.")
    parser.add_argument(
        "--delete-webhook",
        action="store_true",
        help="Delete any configured Telegram webhook so polling can receive messages.",
    )
    parser.add_argument(
        "--drop-pending",
        action="store_true",
        help="Drop pending Telegram updates when deleting the webhook.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.telegram_token:
        print("telegram: TELEGRAM_TOKEN is missing in this shell or .env")
        return 1

    bot = Bot(settings.telegram_token)
    me = await bot.get_me()
    print(f"telegram: token ok, bot=@{me.username or me.first_name}")

    webhook = await bot.get_webhook_info()
    print(f"telegram: webhook_url={'set' if webhook.url else 'empty'}")
    print(f"telegram: pending_update_count={webhook.pending_update_count}")
    if webhook.last_error_message:
        print(f"telegram: last_error={webhook.last_error_message}")

    if args.delete_webhook:
        await bot.delete_webhook(drop_pending_updates=args.drop_pending)
        print(f"telegram: webhook deleted, drop_pending={args.drop_pending}")

    if not webhook.url or args.delete_webhook:
        updates = await bot.get_updates(limit=5, timeout=1)
        print(f"telegram: get_updates returned {len(updates)} update(s)")
        for update in updates:
            message = update.effective_message
            chat = update.effective_chat
            if message and chat:
                text = message.text or "<non-text>"
                print(f"telegram: update chat_id={chat.id} text={text[:80]!r}")
    else:
        print("telegram: polling cannot receive updates while webhook_url is set")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
