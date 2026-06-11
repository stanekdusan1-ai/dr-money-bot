from __future__ import annotations

import re
from app.core.models import Category, InvestmentType

_CATEGORY_KEYWORDS: list[tuple[Category, list[str]]] = [
    (Category.private_equity, ["private equity", "equity", "beteiligung", "share deal", "mehrheit", "minderheit"]),
    (Category.project_finance, ["projekt", "projektfinanzierung", "project finance", "bauprojekt", "development"]),
    (Category.energy, ["windrad", "windräder", "windpark", "solar", "photovoltaik", "pv", "wasserstoff", "biogas", "energie", "kraftwerk"]),
    (Category.industry_machines, ["maschine", "maschinen", "anlage", "produktionsanlage", "cnc", "roboter", "industrieanlage", "verpackungsmaschine"]),
    (Category.products, ["produkt", "erfindung", "patent", "neu auf dem markt", "innovatives produkt", "teuer"]),
    (Category.hotels, ["hotel", "resort", "pension", "tourismus", "wellness"]),
    (Category.real_estate, ["immobilie", "grundstück", "renditeimmobilie", "gewerbeimmobilie", "haus", "villa", "insel", "wald", "acker"]),
    (Category.sponsoring, ["sponsoring", "sponsor", "verein", "team", "sport", "polo", "rennteam"]),
    (Category.startups, ["startup", "seed", "series a", "venture", "wachstumskapital"]),
    (Category.vehicles, ["auto", "oldtimer", "bagger", "traktor", "lkw", "transporter", "baumaschine", "kran", "fuhrpark"]),
    (Category.yachts_boats, ["yacht", "boot", "schiff", "fähre", "marine", "hafen"]),
    (Category.aviation, ["flugzeug", "helikopter", "business jet", "luftfahrt", "aviation"]),
    (Category.horses, ["pferd", "pferde", "pferdesport", "stall", "pferdetransporter"]),
    (Category.agriculture_land, ["landwirtschaft", "obst", "gemüse", "gewächshaus", "ackerland", "forst", "wald"]),
    (Category.healthcare_care, ["pflegeheim", "klinik", "behindertenheim", "seniorenheim", "medizin", "healthcare"]),
    (Category.construction, ["bau", "baumaterial", "fenster", "türen", "zelt", "beton", "tunnel", "straße"]),
    (Category.logistics, ["logistik", "lager", "container", "spedition", "transport", "warehouse"]),
    (Category.technology, ["ki", "ai", "software", "robotik", "technologie", "saas"]),
    (Category.social_projects, ["sozialprojekt", "obdachlosenhilfe", "forschung", "gemeinnützig"]),
    (Category.companies, ["unternehmen", "firma", "nachfolge", "verkauf", "akquisition", "kaufen"]),
]

_INVESTMENT_KEYWORDS: list[tuple[InvestmentType, list[str]]] = [
    (InvestmentType.private_equity, ["private equity", "equity", "beteiligung"]),
    (InvestmentType.venture_capital, ["venture", "startup", "seed", "series a", "vc"]),
    (InvestmentType.majority_stake, ["mehrheit", "mehrheitsbeteiligung"]),
    (InvestmentType.minority_stake, ["minderheit", "minderheitsbeteiligung"]),
    (InvestmentType.joint_venture, ["joint venture", "partnerschaft"]),
    (InvestmentType.project_finance, ["projektfinanzierung", "project finance", "projekt"]),
    (InvestmentType.mezzanine, ["mezzanine"]),
    (InvestmentType.loan, ["darlehen", "kredit", "finanzierung"]),
    (InvestmentType.acquisition, ["übernahme", "akquisition", "firmenkauf", "kaufen"]),
    (InvestmentType.succession, ["nachfolge", "unternehmensnachfolge"]),
    (InvestmentType.restructuring, ["sanierung", "restrukturierung"]),
    (InvestmentType.sponsorship, ["sponsoring", "sponsor"]),
    (InvestmentType.product_purchase, ["maschine", "anlage", "produkt", "windrad", "windräder"]),
    (InvestmentType.off_market, ["off market", "nicht öffentlich", "privat"]),
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def classify_category(text: str) -> Category:
    t = _norm(text)
    for category, keywords in _CATEGORY_KEYWORDS:
        if any(k in t for k in keywords):
            return category
    return Category.unknown


def classify_investment_type(text: str) -> InvestmentType:
    t = _norm(text)
    for inv_type, keywords in _INVESTMENT_KEYWORDS:
        if any(k in t for k in keywords):
            return inv_type
    return InvestmentType.unknown


def all_categories_text() -> str:
    return ", ".join(c.value for c in Category if c != Category.unknown)
