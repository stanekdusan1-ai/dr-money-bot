from __future__ import annotations

from dataclasses import dataclass
from app.core.models import Category, SearchTask


@dataclass(frozen=True)
class SpecialistAgent:
    name: str
    categories: tuple[Category, ...]
    mission: str
    search_patterns: tuple[str, ...]


AGENTS: tuple[SpecialistAgent, ...] = (
    SpecialistAgent("Private-Equity-Scout", (Category.private_equity, Category.companies), "Beteiligungen, Nachfolge, Firmenkäufe und Kapitalbedarf finden.", ("{country} Unternehmen Beteiligung gesucht", "{country} Unternehmensnachfolge Investor gesucht")),
    SpecialistAgent("Projektfinanzierungs-Scout", (Category.project_finance, Category.construction, Category.real_estate), "Bau-, Infrastruktur- und Entwicklungsprojekte mit Kapitalbedarf finden.", ("{country} Projektfinanzierung gesucht", "{country} Bauprojekt Investor gesucht")),
    SpecialistAgent("Hotel-Scout", (Category.hotels,), "Hotels, Resorts und Tourismusbetriebe mit Verkaufs-, Kapital- oder Partnerschaftsbedarf finden.", ("{country} Hotel Investor gesucht", "{country} Hotel Nachfolge Verkauf")),
    SpecialistAgent("Energie-Scout", (Category.energy,), "Solarparks, Windparks, Windräder, Biogas, Wasserstoff und Energieprojekte finden.", ("{country} Windpark Investor gesucht", "{country} Solarpark Projektfinanzierung")),
    SpecialistAgent("Maschinen-Scout", (Category.industry_machines, Category.products), "Teure Maschinen, Industrieanlagen, Produktionsanlagen und neue industrielle Produkte finden.", ("{country} Produktionsanlage Investor gesucht", "{country} Maschinenhersteller Kapital gesucht")),
    SpecialistAgent("Fahrzeug-Scout", (Category.vehicles, Category.logistics), "Nutzfahrzeuge, Baumaschinen, LKW-Flotten und Logistikunternehmen finden.", ("{country} Logistik Unternehmen Nachfolge", "{country} Baumaschinen Verkauf Firma")),
    SpecialistAgent("Luxus-Scout", (Category.yachts_boats, Category.aviation, Category.horses, Category.luxury_assets), "Yachten, Flugzeuge, Pferde, Luxusassets und private Verkäufer finden.", ("{country} Yacht Investor Verkauf", "{country} Pferdesport Sponsor Investor")),
    SpecialistAgent("Healthcare-Scout", (Category.healthcare_care,), "Pflegeheime, Kliniken, Medizintechnik und Care-Projekte finden.", ("{country} Pflegeheim Investor gesucht", "{country} Klinik Beteiligung gesucht")),
    SpecialistAgent("Innovation-Ideen-Agent", (Category.innovation_ideas, Category.technology, Category.products), "Neue lukrative Produkte, Patente, Trends und Technologien entdecken, die zu den Investmentkategorien passen.", ("new lucrative industrial product investment", "emerging profitable technology investment")),
    SpecialistAgent("Sponsoring-Scout", (Category.sponsoring,), "Sponsoringmöglichkeiten ab hohem Budget mit direkten Ansprechpartnern finden.", ("{country} Sponsoring gesucht Sport", "{country} Sponsor gesucht Verein")),
)


def select_agents(task: SearchTask) -> list[SpecialistAgent]:
    if task.category == Category.unknown:
        return list(AGENTS)
    selected = [agent for agent in AGENTS if task.category in agent.categories]
    return selected or list(AGENTS)


def specialist_strategy(task: SearchTask) -> str:
    agents = select_agents(task)
    lines = [f"Suchauftrag: {task.raw_query}", f"Land: {task.country}", f"Kategorie: {task.category.value}", "", "Aktive Agenten:"]
    for agent in agents:
        lines.append(f"- {agent.name}: {agent.mission}")
    lines.append("")
    lines.append("Wichtig: Funde gehen zuerst an Data-Quality/Dublettenprüfung und werden erst danach gespeichert.")
    return "\n".join(lines)
