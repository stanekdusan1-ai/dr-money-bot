from __future__ import annotations

from app.agents.email_agent import EmailAgent
from app.agents.specialists import select_agents, specialist_strategy
from app.core.classifier import classify_category, classify_investment_type
from app.core.country_rules import detect_country_and_language
from app.core.models import CommandResult, Lead, SearchTask
from app.research.search_client import ResearchClient
from app.storage.repository import Repository


class ChefAgent:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo
        self.email_agent = EmailAgent()
        self.research = ResearchClient()

    def create_search_task(self, raw_query: str) -> tuple[SearchTask, str]:
        country, language = detect_country_and_language(raw_query)
        category = classify_category(raw_query)
        investment_type = classify_investment_type(raw_query)
        task = SearchTask(raw_query=raw_query, country=country, language=language, category=category, investment_type=investment_type)
        self.repo.add_task(task)
        return task, specialist_strategy(task)

    def run_search(self, raw_query: str, limit_per_agent: int = 2) -> CommandResult:
        task, strategy = self.create_search_task(raw_query)
        created = merged = 0
        warnings: list[str] = []
        for agent in select_agents(task):
            for lead in self.research.search(task, agent, limit=limit_per_agent):
                result = self.repo.upsert_lead(lead)
                if result.action == "created":
                    created += 1
                else:
                    merged += 1
                warnings.extend(result.warnings)
        message = (
            f"Suche gestartet und Demo-Ergebnisse gespeichert.\n"
            f"Neue Leads: {created}\nZusammengeführte Dubletten: {merged}\n\n{strategy}"
        )
        return CommandResult(message=message, payload={"task_id": task.id, "created": created, "merged": merged, "warnings": warnings[:20]})

    def create_email_draft_for_latest_task(self) -> str:
        tasks = self.repo.list_tasks()
        if not tasks:
            return "Es gibt noch keinen Suchauftrag. Nutze zuerst /suche ..."
        task = tasks[-1]
        draft = self.email_agent.draft_for_task(task)
        self.repo.add_email_draft(draft)
        return f"E-Mail-Entwurf erstellt:\n\nBetreff: {draft.subject}\n\n{draft.body}"

    def create_email_draft_for_lead(self, lead_id: str) -> str:
        leads = self.repo.list_leads()
        lead = next((item for item in leads if item.id == lead_id), None)
        if not lead:
            return "Lead nicht gefunden."
        draft = self.email_agent.draft_for_lead(lead)
        self.repo.add_email_draft(draft)
        return f"E-Mail-Entwurf für {lead.company_name} erstellt:\n\nBetreff: {draft.subject}\n\n{draft.body}"

    def save_manual_lead(self, company_name: str, website: str | None = None, email: str | None = None, phone: str | None = None, activity: str | None = None, country: str = "unbekannt") -> Lead:
        tasks = self.repo.list_tasks()
        task = tasks[-1] if tasks else None
        lead = Lead(
            company_name=company_name,
            website=website,
            contact_email=email,
            phone=phone,
            activity=activity,
            task_id=task.id if task else None,
            country=country if country != "unbekannt" else (task.country if task else "unbekannt"),
            category=task.category if task else "unknown",
            investment_type=task.investment_type if task else "unknown",
        )
        return self.repo.upsert_lead(lead).lead

    def database_summary(self) -> str:
        leads = self.repo.list_leads()
        tasks = self.repo.list_tasks()
        drafts = self.repo.list_email_drafts()
        avg_quality = round(sum(l.quality_score for l in leads) / len(leads), 1) if leads else 0
        return f"Tasks: {len(tasks)} | Leads: {len(leads)} | E-Mail-Entwürfe: {len(drafts)} | Ø Datenqualität: {avg_quality}%"
