import os
import re
from dataclasses import dataclass

from config.settings import get_settings


@dataclass(frozen=True)
class TranslationResult:
    detected_lang: str
    translated_text: str


def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    return "es"


async def translate_text(text: str, target_language: str = "zh") -> TranslationResult:
    detected_lang = detect_language(text)
    settings = get_settings()

    if detected_lang == target_language:
        return TranslationResult(detected_lang=detected_lang, translated_text=text)

    provider = settings.translation_provider.lower()
    if provider == "google":
        translated_text = await translate_with_google(text, target_language)
    elif provider == "llm":
        translated_text = await translate_with_llm(text, target_language)
    else:
        translated_text = text

    return TranslationResult(detected_lang=detected_lang, translated_text=translated_text)


async def translate_with_google(text: str, target_language: str) -> str:
    settings = get_settings()
    if not settings.google_application_credentials:
        return text

    try:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
        )
        from google.cloud import translate_v2 as translate

        client = translate.Client()
        result = client.translate(text, target_language=target_language)
        return result.get("translatedText", text)
    except Exception:
        return text


async def translate_with_llm(text: str, target_language: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return text

    language_name = {"zh": "Chinese", "es": "Spanish"}.get(target_language, target_language)
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a translation engine for humanitarian rescue coordination. "
                        "Translate faithfully and return only the translation."
                    ),
                },
                {"role": "user", "content": f"Translate to {language_name}:\n{text}"},
            ],
            temperature=0,
            max_tokens=500,
        )
        return (response.choices[0].message.content or text).strip()
    except Exception:
        return text
