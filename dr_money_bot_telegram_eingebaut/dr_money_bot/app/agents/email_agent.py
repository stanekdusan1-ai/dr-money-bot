from __future__ import annotations

from app.core.models import EmailDraft, Lead, SearchTask


class EmailAgent:
    def draft_for_task(self, task: SearchTask) -> EmailDraft:
        subject = f"Diskrete Anfrage: {task.category.value} / {task.country}"
        body = (
            "Guten Tag,\n\n"
            "wir prüfen derzeit ausgewählte Investment-, Beteiligungs- und Projektmöglichkeiten. "
            f"Ihr Bereich passt möglicherweise zu unserem aktuellen Suchprofil ({task.raw_query}).\n\n"
            "Falls grundsätzlich Interesse an einem diskreten Austausch über Kapital, Beteiligung, "
            "Projektfinanzierung, Nachfolge oder Partnerschaft besteht, freue ich mich über eine kurze Rückmeldung.\n\n"
            "Freundliche Grüße\nMilan Bubenik"
        )
        return EmailDraft(subject=subject, body=body, language=task.language)

    def draft_for_lead(self, lead: Lead) -> EmailDraft:
        subject = f"Diskrete Investmentanfrage – {lead.company_name}"
        greeting = f"Guten Tag {lead.contact_person}," if lead.contact_person else "Guten Tag,"
        body = (
            f"{greeting}\n\n"
            f"wir sind auf {lead.company_name} aufmerksam geworden. Der Tätigkeitsbereich ({lead.activity or lead.category.value}) "
            "könnte zu unserem aktuellen Investmentprofil passen.\n\n"
            "Wir prüfen diskret Möglichkeiten in den Bereichen Beteiligung, Finanzierung, Projektentwicklung, "
            "Unternehmensnachfolge, hochwertige Assets und strategische Partnerschaften.\n\n"
            "Falls ein Gespräch grundsätzlich interessant ist, freue ich mich über eine kurze Rückmeldung oder einen passenden Ansprechpartner.\n\n"
            "Freundliche Grüße\nMilan Bubenik"
        )
        return EmailDraft(lead_id=lead.id, to_email=lead.contact_email, subject=subject, body=body, language="de")
