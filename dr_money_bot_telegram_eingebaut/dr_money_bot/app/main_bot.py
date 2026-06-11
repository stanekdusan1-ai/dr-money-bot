from __future__ import annotations

from telegram.ext import ApplicationBuilder, CommandHandler

from app.core.config import settings
from app.telegram.handlers import (
    categories_command,
    help_command,
    leads_command,
    mail_command,
    manual_lead_command,
    search_command,
    start,
    status_command,
)


def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN fehlt in .env")
    app = ApplicationBuilder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hilfe", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("branchen", categories_command))
    app.add_handler(CommandHandler("suche", search_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("leads", leads_command))
    app.add_handler(CommandHandler("mail", mail_command))
    app.add_handler(CommandHandler("lead", manual_lead_command))
    app.run_polling()


if __name__ == "__main__":
    main()
