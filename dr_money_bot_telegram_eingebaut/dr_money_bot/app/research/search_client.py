from __future__ import annotations

from urllib.parse import urlparse

import httpx

from app.agents.specialists import SpecialistAgent
from app.core.config import settings
from app.core.models import Category, Lead, SourceRecord, SearchTask


class ResearchClient:
    """Recherche-Schnittstelle für DR Money Bot.

    Unterstützt aktuell:
    - mock: sichere Demo-Daten
    - serper: echte Google-Suchergebnisse über Serper API

    Firecrawl ist bereits in der .env vorbereitet. Die eigentliche Webseiten-Extraktion
    kann im nächsten Schritt ergänzt werden, sobald die Google-Suche stabil läuft.
    """

    def search(self, task: SearchTask, agent: SpecialistAgent, limit: int = 5) -> list[Lead]:
        provider = (settings.search_provider or "mock").lower().strip()
        if provider == "serper" and settings.serper_api_key:
            try:
                leads = self._search_with_serper(task=task, agent=agent, limit=limit)
                if leads:
                    return leads
            except Exception as exc:  # bewusst robust: Bot soll nicht komplett abbrechen
                return self._mock_search(task, agent, limit, note=f"Serper-Fehler/Fallback: {exc}")
        return self._mock_search(task, agent, limit)

    def _build_query(self, task: SearchTask, agent: SpecialistAgent) -> str:
        country = "" if task.country == "unbekannt" else task.country
        category = task.category.value if task.category != Category.unknown else agent.name
        base = task.raw_query.strip()
        intent_words = "Investment Kapitalbedarf Beteiligung Verkauf Finanzierung Kontakt"
        return " ".join(part for part in [base, category, country, intent_words] if part).strip()

    def _search_with_serper(self, task: SearchTask, agent: SpecialistAgent, limit: int) -> list[Lead]:
        query = self._build_query(task, agent)
        payload = {"q": query, "num": max(1, min(limit, 10)), "gl": "de", "hl": task.language or "de"}
        headers = {"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"}

        with httpx.Client(timeout=30) as client:
            response = client.post("https://google.serper.dev/search", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        organic = data.get("organic") or []
        country = task.country if task.country != "unbekannt" else "International"
        category = task.category if task.category != Category.unknown else agent.categories[0]
        leads: list[Lead] = []

        for item in organic[:limit]:
            url = item.get("link") or item.get("url")
            title = (item.get("title") or "Unbekannter Lead").strip()
            snippet = (item.get("snippet") or "").strip()
            if not url:
                continue

            domain = urlparse(url).netloc.replace("www.", "")
            company_name = self._clean_company_name(title=title, domain=domain)
            leads.append(
                Lead(
                    task_id=task.id,
                    company_name=company_name,
                    activity=snippet or agent.mission,
                    category=category,
                    investment_type=task.investment_type,
                    website=url,
                    domain=domain,
                    country=country,
                    capital_need=True,
                    capital_need_text=f"Gefunden über Serper-Suche: {query}",
                    source="serper_google_search",
                    sources=[
                        SourceRecord(
                            url=url,
                            title=title,
                            snippet=snippet,
                            found_by_agent=agent.name,
                        )
                    ],
                    tags=[agent.name, category.value, "serper"],
                    notes="Echter Suchtreffer. Bitte vor Kontaktaufnahme manuell prüfen.",
                )
            )
        return leads

    def _clean_company_name(self, title: str, domain: str) -> str:
        separators = [" | ", " - ", " – ", " — ", ": "]
        cleaned = title.strip()
        for sep in separators:
            if sep in cleaned:
                cleaned = cleaned.split(sep)[0].strip()
        if not cleaned and domain:
            cleaned = domain.split(".")[0].replace("-", " ").title()
        return cleaned or "Unbekannter Lead"

    def _mock_search(self, task: SearchTask, agent: SpecialistAgent, limit: int = 3, note: str | None = None) -> list[Lead]:
        country = task.country if task.country != "unbekannt" else "International"
        category = task.category if task.category != Category.unknown else agent.categories[0]
        samples: list[Lead] = []
        for i in range(1, limit + 1):
            company = f"Demo {agent.name.replace('-', ' ')} Opportunity {i}"
            domain = company.lower().replace(" ", "-").replace("ä", "ae") + ".example.com"
            samples.append(
                Lead(
                    task_id=task.id,
                    company_name=company,
                    activity=agent.mission,
                    category=category,
                    investment_type=task.investment_type,
                    website=f"https://{domain}",
                    contact_email=f"info@{domain}",
                    phone=f"+41 41 000 00 {i:02d}",
                    address=f"Beispielstrasse {i}",
                    city="Zielmarkt",
                    country=country,
                    ceo=f"CEO Beispiel {i}",
                    contact_person=f"Kontakt Beispiel {i}",
                    capital_need=True,
                    capital_need_text=f"Möglicher Kapital-/Partnerbedarf laut Suchmuster: {task.raw_query}",
                    estimated_ticket_size=1_000_000 * i,
                    source="demo_research_client",
                    sources=[
                        SourceRecord(
                            url=f"https://{domain}",
                            title=company,
                            snippet=agent.mission,
                            found_by_agent=agent.name,
                        )
                    ],
                    tags=[agent.name, category.value],
                    notes=note or "Demo-Datensatz: zeigt Datenstruktur und Dublettenprüfung. Für echte Recherche API-Key anschließen.",
                )
            )
        return samples
