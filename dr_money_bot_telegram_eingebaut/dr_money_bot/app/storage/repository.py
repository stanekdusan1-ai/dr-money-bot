from __future__ import annotations

from abc import ABC, abstractmethod
from app.core.models import EmailDraft, IngestResult, Lead, SearchTask


class Repository(ABC):
    @abstractmethod
    def add_task(self, task: SearchTask) -> SearchTask: ...

    @abstractmethod
    def list_tasks(self) -> list[SearchTask]: ...

    @abstractmethod
    def upsert_lead(self, lead: Lead) -> IngestResult: ...

    def add_lead(self, lead: Lead) -> Lead:
        return self.upsert_lead(lead).lead

    @abstractmethod
    def list_leads(self) -> list[Lead]: ...

    @abstractmethod
    def add_email_draft(self, draft: EmailDraft) -> EmailDraft: ...

    @abstractmethod
    def list_email_drafts(self) -> list[EmailDraft]: ...
