from __future__ import annotations

import re
from urllib.parse import urlparse
from app.core.models import IngestResult, Lead, LeadStatus, now_iso

_COMPANY_SUFFIXES = [
    "gmbh", "ag", "kg", "ug", "mbh", "ltd", "limited", "inc", "llc", "sarl", "s.r.l", "srl", "sa", "spa", "bv", "oy", "ab", "sas"
]


def normalize_domain(website: str | None) -> str | None:
    if not website:
        return None
    value = website.strip().lower()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    host = parsed.netloc or parsed.path
    host = host.replace("www.", "").split("/")[0]
    return host or None


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    cleaned = re.sub(r"[^0-9+]", "", phone)
    return cleaned or None


def normalize_company_name(name: str) -> str:
    text = name.lower().strip()
    text = re.sub(r"[.,'’`´()\[\]&/-]", " ", text)
    words = [w for w in text.split() if w not in _COMPANY_SUFFIXES]
    return " ".join(words)


def email_domain(email: str | None) -> str | None:
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].lower().strip()


def duplicate_key(lead: Lead) -> str:
    domain = normalize_domain(lead.website) or email_domain(str(lead.contact_email) if lead.contact_email else None)
    phone = normalize_phone(lead.phone)
    name = normalize_company_name(lead.company_name)
    country = (lead.country or "").lower().strip()
    if domain:
        return f"domain:{domain}"
    if phone and name:
        return f"phone_name:{phone}:{name}"
    return f"name_country:{name}:{country}"


def enrich_and_score(lead: Lead) -> tuple[Lead, list[str]]:
    warnings: list[str] = []
    lead.domain = normalize_domain(lead.website)
    lead.phone = normalize_phone(lead.phone)
    lead.duplicate_key = duplicate_key(lead)

    score = 0
    required = {"company_name": lead.company_name, "website/domain": lead.website or lead.domain, "country": lead.country, "category": lead.category.value}
    for field_name, value in required.items():
        if value and value != "unbekannt" and value != "unknown":
            score += 15
        else:
            warnings.append(f"Pflicht-/Kernfeld fehlt oder ist unklar: {field_name}")

    optional_fields = [
        lead.contact_email, lead.phone, lead.address, lead.ceo, lead.contact_person,
        lead.activity, lead.uid_vat, lead.linkedin, lead.capital_need_text
    ]
    score += sum(5 for item in optional_fields if item)
    if lead.sources:
        score += min(15, len(lead.sources) * 5)
    lead.quality_score = min(score, 100)

    inv_score = 0
    if lead.capital_need:
        inv_score += 30
    if lead.capital_need_text:
        inv_score += 20
    if lead.estimated_ticket_size:
        inv_score += 15
    if lead.category.value not in ["unknown"]:
        inv_score += 15
    if lead.investment_type.value != "unknown":
        inv_score += 10
    if lead.contact_email or lead.phone:
        inv_score += 10
    lead.investment_score = min(inv_score, 100)

    lead.status = LeadStatus.qualified if lead.quality_score >= 60 else LeadStatus.needs_review
    lead.updated_at = now_iso()
    if not lead.last_verified and lead.quality_score >= 60:
        lead.last_verified = now_iso()
    return lead, warnings


def merge_leads(existing: Lead, incoming: Lead) -> tuple[Lead, list[str]]:
    changed: list[str] = []
    for field in incoming.__class__.model_fields:
        if field in {"id", "created_at", "quality_score", "investment_score", "duplicate_key", "status"}:
            continue
        old = getattr(existing, field)
        new = getattr(incoming, field)
        if field == "sources":
            urls = {s.url for s in existing.sources if s.url}
            for source in incoming.sources:
                if not source.url or source.url not in urls:
                    existing.sources.append(source)
                    changed.append("sources")
            continue
        if field == "tags":
            merged = list(dict.fromkeys(existing.tags + incoming.tags))
            if merged != existing.tags:
                existing.tags = merged
                changed.append("tags")
            continue
        if (old is None or old == "" or old == "unbekannt" or old == "unknown") and new not in (None, "", "unbekannt", "unknown"):
            setattr(existing, field, new)
            changed.append(field)
    existing.updated_at = now_iso()
    return existing, sorted(set(changed))
