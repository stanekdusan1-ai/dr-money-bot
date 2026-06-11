from __future__ import annotations

from app.agents.chef_agent import ChefAgent
from app.core.classifier import all_categories_text
from app.storage.factory import get_repository

HELP_TEXT = """
DR Money Bot Befehle:
/start - Start
/hilfe - Hilfe
/branchen - alle Kategorien
/suche <Thema/Land/Budget> - Agenten starten und Leads speichern
/status - Datenbankstatus
/leads - letzte Leads anzeigen
/mail - Mailentwurf für letzten Suchauftrag
/lead Name | Website | Email | Telefon | Tätigkeit | Land - manuellen Lead speichern

Beispiele:
/suche windräder spanien projektfinanzierung
/suche private equity unternehmensnachfolge deutschland
/suche teure maschinen schweiz kapitalbedarf
/suche neue lukrative produkte energie europa
""".strip()


def get_agent() -> ChefAgent:
    return ChefAgent(get_repository())


async def start(update, context) -> None:
    await update.message.reply_text("Willkommen beim DR Money Bot. Nutze /hilfe oder /suche ...")


async def help_command(update, context) -> None:
    await update.message.reply_text(HELP_TEXT)


async def categories_command(update, context) -> None:
    await update.message.reply_text("Kategorien:\n" + all_categories_text())


async def search_command(update, context) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Bitte nutze: /suche <Thema/Land/Budget>")
        return
    result = get_agent().run_search(query)
    await update.message.reply_text(result.message[:3900])


async def status_command(update, context) -> None:
    await update.message.reply_text(get_agent().database_summary())


async def leads_command(update, context) -> None:
    leads = get_repository().list_leads()[-10:]
    if not leads:
        await update.message.reply_text("Noch keine Leads gespeichert.")
        return
    lines = []
    for lead in leads:
        lines.append(f"• {lead.company_name} | {lead.country} | {lead.category.value} | Qualität {lead.quality_score}% | {lead.contact_email or lead.phone or lead.website or 'kein Kontakt'}")
    await update.message.reply_text("Letzte Leads:\n" + "\n".join(lines))


async def mail_command(update, context) -> None:
    await update.message.reply_text(get_agent().create_email_draft_for_latest_task()[:3900])


async def manual_lead_command(update, context) -> None:
    raw = " ".join(context.args).strip()
    if not raw:
        await update.message.reply_text("Format: /lead Name | Website | Email | Telefon | Tätigkeit | Land")
        return
    parts = [p.strip() for p in raw.split("|")]
    while len(parts) < 6:
        parts.append(None)
    lead = get_agent().save_manual_lead(company_name=parts[0], website=parts[1], email=parts[2], phone=parts[3], activity=parts[4], country=parts[5] or "unbekannt")
    await update.message.reply_text(f"Lead gespeichert/geprüft: {lead.company_name}\nDatenqualität: {lead.quality_score}%\nDubletten-Key: {lead.duplicate_key}")
