import os

from fastapi import FastAPI
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot import handlers
from config.settings import get_settings
from models.database import init_db

api = FastAPI(title="ArcaVida", version="0.2.0")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def build_application() -> Application:
    settings = get_settings()
    settings.validate_runtime_security()
    if not settings.telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN is required to start the Telegram bot")

    application = Application.builder().token(settings.telegram_token).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("briefing", handlers.briefing))
    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(CommandHandler("verify", handlers.verify))
    application.add_handler(CommandHandler("dispatch", handlers.dispatch))
    application.add_handler(CommandHandler("close", handlers.close))
    application.add_handler(CommandHandler("note", handlers.note))
    application.add_handler(CommandHandler("need", handlers.need))
    application.add_handler(CommandHandler("deliver", handlers.deliver))
    application.add_handler(CommandHandler("shortage", handlers.shortage))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))
    return application


def main() -> None:
    settings = get_settings()
    settings.validate_runtime_security()
    init_db()
    application = build_application()
    if settings.webhook_url:
        port = int(os.getenv("PORT", "8080"))
        token_path = settings.webhook_secret_path or "webhook"
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token_path,
            webhook_url=f"{settings.webhook_url.rstrip('/')}/{token_path}",
        )
    else:
        application.run_polling()


if __name__ == "__main__":
    main()
