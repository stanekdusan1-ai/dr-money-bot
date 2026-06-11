from __future__ import annotations

from app.core.models import EmailDraft, IngestResult, Lead, SearchTask
from app.services.data_quality import duplicate_key, enrich_and_score, merge_leads
from app.storage.repository import Repository


def _value(value):
    if hasattr(value, "value"):
        return value.value
    return value


class SupabaseRepository(Repository):
    """Supabase-Speicher für die Tabellen leads, search_runs und emails."""

    def __init__(self, url: str, service_key: str) -> None:
        if not url or not service_key:
            raise ValueError("SUPABASE_URL und SUPABASE_SERVICE_KEY fehlen.")
        from supabase import create_client

        # Falls aus Supabase versehentlich die REST-URL kopiert wurde, korrigieren wir sie automatisch.
        self.url = url.rstrip("/").replace("/rest/v1", "")
        self.client = create_client(self.url, service_key)

    def add_task(self, task: SearchTask) -> SearchTask:
        payload = {
            "id": task.id,
            "query": task.raw_query,
            "category": _value(task.category),
            "region": task.region or task.country,
            "results_count": 0,
            "status": task.status,
            "notes": task.notes,
        }
        self.client.table("search_runs").insert(payload).execute()
        return task

    def list_tasks(self) -> list[SearchTask]:
        res = self.client.table("search_runs").select("*").order("created_at", desc=False).execute()
        tasks: list[SearchTask] = []
        for row in res.data or []:
            tasks.append(
                SearchTask(
                    id=str(row.get("id")),
                    raw_query=row.get("query") or "",
                    country=row.get("region") or "unbekannt",
                    region=row.get("region"),
                    category=row.get("category") or "unknown",
                    status=row.get("status") or "created",
                    notes=row.get("notes") or "",
                )
            )
        return tasks

    def _lead_to_row(self, lead: Lead) -> dict:
        return {
            "id": lead.id,
            "category": _value(lead.category),
            "title": lead.company_name,
            "company_name": lead.company_name,
            "contact_name": lead.contact_person or lead.ceo,
            "email": str(lead.contact_email) if lead.contact_email else None,
            "phone": lead.phone,
            "website": lead.website,
            "country": lead.country,
            "city": lead.city,
            "deal_type": _value(lead.investment_type),
            "estimated_value": lead.estimated_ticket_size,
            "currency": "EUR",
            "source_url": lead.source or (lead.sources[0].url if lead.sources else None),
            "status": _value(lead.status),
            "score": max(lead.quality_score or 0, lead.investment_score or 0),
            "notes": lead.notes or lead.activity or "",
        }

    def _row_to_lead(self, row: dict) -> Lead:
        return Lead(
            id=str(row.get("id")),
            company_name=row.get("company_name") or row.get("title") or "Unbekannter Lead",
            category=row.get("category") or "unknown",
            investment_type=row.get("deal_type") or "unknown",
            website=row.get("website"),
            contact_email=row.get("email"),
            phone=row.get("phone"),
            city=row.get("city"),
            country=row.get("country") or "unbekannt",
            contact_person=row.get("contact_name"),
            estimated_ticket_size=row.get("estimated_value"),
            source=row.get("source_url"),
            quality_score=row.get("score") or 0,
            investment_score=row.get("score") or 0,
            status=row.get("status") or "new",
            notes=row.get("notes") or "",
        )

    def upsert_lead(self, lead: Lead) -> IngestResult:
        lead, warnings = enrich_and_score(lead)
        incoming_key = lead.duplicate_key or duplicate_key(lead)
        existing_leads = self.list_leads()

        for existing in existing_leads:
            existing_key = existing.duplicate_key or duplicate_key(existing)
            if existing_key == incoming_key:
                merged, changed = merge_leads(existing, lead)
                merged, more_warnings = enrich_and_score(merged)
                self.client.table("leads").update(self._lead_to_row(merged)).eq("id", existing.id).execute()
                return IngestResult(
                    action="merged_duplicate",
                    lead=merged,
                    matched_existing_id=existing.id,
                    warnings=warnings + more_warnings,
                    changed_fields=changed,
                )

        self.client.table("leads").insert(self._lead_to_row(lead)).execute()
        return IngestResult(action="created", lead=lead, warnings=warnings)

    def list_leads(self) -> list[Lead]:
        res = self.client.table("leads").select("*").order("created_at", desc=False).execute()
        return [self._row_to_lead(row) for row in (res.data or [])]

    def add_email_draft(self, draft: EmailDraft) -> EmailDraft:
        payload = {
            "id": draft.id,
            "lead_id": draft.lead_id,
            "email_to": str(draft.to_email) if draft.to_email else None,
            "subject": draft.subject,
            "body": draft.body,
            "status": "draft",
        }
        self.client.table("emails").insert(payload).execute()
        return draft

    def list_email_drafts(self) -> list[EmailDraft]:
        res = self.client.table("emails").select("*").order("created_at", desc=False).execute()
        drafts: list[EmailDraft] = []
        for row in res.data or []:
            drafts.append(
                EmailDraft(
                    id=str(row.get("id")),
                    lead_id=row.get("lead_id"),
                    to_email=row.get("email_to"),
                    subject=row.get("subject") or "",
                    body=row.get("body") or "",
                    sent=(row.get("status") == "sent"),
                )
            )
        return drafts
