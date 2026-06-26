#!/usr/bin/env python

import argparse
import asyncio
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from telegram import Bot

from config.settings import get_settings
from core.extractor import extract_info
from core.translator import translate_text

SAMPLE_ES = "Ubicación: Caracas Centro. Hay una familia atrapada, necesita agua y comida."


def mask(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"set:{value[:4]}...{value[-4:]}"


async def check_telegram() -> bool:
    settings = get_settings()
    if not settings.telegram_token:
        print("telegram: skipped, TELEGRAM_TOKEN is missing")
        return False

    bot = Bot(settings.telegram_token)
    me = await bot.get_me()
    print(f"telegram: ok, bot=@{me.username or me.first_name}")
    return True


async def check_translate() -> bool:
    settings = get_settings()
    if settings.translation_provider == "google" and not settings.google_application_credentials:
        print("translate: skipped, GOOGLE_APPLICATION_CREDENTIALS is missing")
        return False
    if settings.translation_provider == "llm" and not settings.openai_api_key:
        print("translate: skipped, OPENAI_API_KEY is missing for TRANSLATION_PROVIDER=llm")
        return False
    if settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
        )

    result = await translate_text(SAMPLE_ES)
    if result.translated_text == SAMPLE_ES:
        print("translate: failed, translation returned original text")
        return False
    print(
        f"translate: ok, provider={settings.translation_provider}, detected={result.detected_lang}, sample={result.translated_text[:80]}"
    )
    return True


async def check_llm() -> bool:
    settings = get_settings()
    if not settings.openai_api_key:
        print("llm: skipped, OPENAI_API_KEY is missing")
        return False

    result = await extract_info(SAMPLE_ES, use_llm=True)
    print(
        "llm: ok, "
        f"model={settings.openai_model}, location={result.location}, "
        f"priority={result.priority}, needs={','.join(result.needs)}"
    )
    return True


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run live ArcaVida integration smoke checks.")
    parser.add_argument(
        "checks",
        nargs="*",
        choices=["telegram", "translate", "llm", "all"],
        default=["all"],
    )
    args = parser.parse_args()

    settings = get_settings()
    settings.validate_runtime_security()
    selected = {"telegram", "translate", "llm"} if "all" in args.checks else set(args.checks)

    print("loaded env:")
    print(f"  TELEGRAM_TOKEN={mask(settings.telegram_token)}")
    print(f"  GOOGLE_APPLICATION_CREDENTIALS={mask(settings.google_application_credentials)}")
    print(f"  TRANSLATION_PROVIDER={settings.translation_provider}")
    print(f"  OPENAI_API_KEY={mask(settings.openai_api_key)}")
    print(f"  OPENAI_BASE_URL={settings.openai_base_url or 'default'}")
    print(f"  OPENAI_MODEL={settings.openai_model}")

    checks = []
    if "telegram" in selected:
        checks.append(await check_telegram())
    if "translate" in selected:
        checks.append(await check_translate())
    if "llm" in selected:
        checks.append(await check_llm())

    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
