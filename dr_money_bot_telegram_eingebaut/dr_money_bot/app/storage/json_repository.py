from __future__ import annotations

import json
from pathlib import Path
from typing import Type, TypeVar

from app.core.models import EmailDraft, IngestResult, Lead, SearchTask
from app.services.data_quality import duplicate_key, enrich_and_score, merge_leads
from app.storage.repository import Repository

T = TypeVar("T")


class JsonRepository(Repository):
    def __init__(self, data_dir: str = "data") -> None:
        self.base = Path(data_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        for name in ["tasks.json", "leads.json", "email_drafts.json"]:
            path = self.base / name
            if not path.exists():
                path.write_text("[]", encoding="utf-8")

    def _read(self, file_name: str, model: Type[T]) -> list[T]:
        path = self.base / file_name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Datenbankdatei ist beschädigt: {path}") from exc
        return [model.model_validate(item) for item in data]

    def _write(self, file_name: str, items: list) -> None:
        payload = [item.model_dump(mode="json") for item in items]
        tmp = self.base / f".{file_name}.tmp"
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.base / file_name)

    def add_task(self, task: SearchTask) -> SearchTask:
        items = self.list_tasks()
        items.append(task)
        self._write("tasks.json", items)
        return task

    def list_tasks(self) -> list[SearchTask]:
        return self._read("tasks.json", SearchTask)

    def upsert_lead(self, lead: Lead) -> IngestResult:
        lead, warnings = enrich_and_score(lead)
        leads = self.list_leads()
        incoming_key = lead.duplicate_key or duplicate_key(lead)
        for idx, existing in enumerate(leads):
            existing_key = existing.duplicate_key or duplicate_key(existing)
            if existing_key == incoming_key:
                merged, changed = merge_leads(existing, lead)
                merged, more_warnings = enrich_and_score(merged)
                leads[idx] = merged
                self._write("leads.json", leads)
                return IngestResult(
                    action="merged_duplicate",
                    lead=merged,
                    matched_existing_id=merged.id,
                    warnings=warnings + more_warnings,
                    changed_fields=changed,
                )
        leads.append(lead)
        self._write("leads.json", leads)
        return IngestResult(action="created", lead=lead, warnings=warnings)

    def list_leads(self) -> list[Lead]:
        return self._read("leads.json", Lead)

    def add_email_draft(self, draft: EmailDraft) -> EmailDraft:
        items = self.list_email_drafts()
        items.append(draft)
        self._write("email_drafts.json", items)
        return draft

    def list_email_drafts(self) -> list[EmailDraft]:
        return self._read("email_drafts.json", EmailDraft)
