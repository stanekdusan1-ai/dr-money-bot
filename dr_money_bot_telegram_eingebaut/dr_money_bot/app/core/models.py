from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Category(str, Enum):
    private_equity = "private_equity"
    project_finance = "project_finance"
    companies = "companies"
    startups = "startups"
    hotels = "hotels"
    real_estate = "real_estate"
    sponsoring = "sponsoring"
    products = "products"
    vehicles = "vehicles"
    horses = "horses"
    yachts_boats = "yachts_boats"
    agriculture_land = "agriculture_land"
    healthcare_care = "healthcare_care"
    energy = "energy"
    construction = "construction"
    logistics = "logistics"
    industry_machines = "industry_machines"
    aviation = "aviation"
    luxury_assets = "luxury_assets"
    gastronomy = "gastronomy"
    technology = "technology"
    social_projects = "social_projects"
    innovation_ideas = "innovation_ideas"
    unknown = "unknown"


class InvestmentType(str, Enum):
    private_equity = "private_equity"
    venture_capital = "venture_capital"
    majority_stake = "majority_stake"
    minority_stake = "minority_stake"
    joint_venture = "joint_venture"
    project_finance = "project_finance"
    mezzanine = "mezzanine"
    loan = "loan"
    acquisition = "acquisition"
    asset_deal = "asset_deal"
    share_deal = "share_deal"
    succession = "succession"
    restructuring = "restructuring"
    sponsorship = "sponsorship"
    product_purchase = "product_purchase"
    off_market = "off_market"
    unknown = "unknown"


class LeadStatus(str, Enum):
    new = "new"
    needs_review = "needs_review"
    qualified = "qualified"
    draft_ready = "draft_ready"
    contacted = "contacted"
    replied = "replied"
    follow_up_due = "follow_up_due"
    rejected = "rejected"
    interesting = "interesting"
    duplicate_merged = "duplicate_merged"


class SourceRecord(BaseModel):
    url: str | None = None
    title: str | None = None
    snippet: str | None = None
    found_by_agent: str | None = None
    found_at: str = Field(default_factory=now_iso)


class SearchTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    raw_query: str
    country: str = "unbekannt"
    region: str | None = None
    language: str = "de"
    category: Category = Category.unknown
    investment_type: InvestmentType = InvestmentType.unknown
    budget_min: float | None = None
    budget_max: float | None = None
    goal: str = "Investment-/Kontaktanfrage vorbereiten"
    auto_agents: bool = True
    created_at: str = Field(default_factory=now_iso)
    status: str = "created"
    notes: str = ""


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str | None = None

    company_name: str
    legal_name: str | None = None
    activity: str | None = None
    category: Category = Category.unknown
    investment_type: InvestmentType = InvestmentType.unknown

    website: str | None = None
    domain: str | None = None
    contact_email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str = "unbekannt"

    ceo: str | None = None
    contact_person: str | None = None
    role: str | None = None
    linkedin: str | None = None
    uid_vat: str | None = None
    commercial_register: str | None = None

    employees: int | None = None
    revenue: float | None = None
    capital_need: bool | None = None
    capital_need_text: str | None = None
    estimated_ticket_size: float | None = None

    source: str | None = None
    sources: list[SourceRecord] = Field(default_factory=list)
    quality_score: int = 0
    investment_score: int = 0
    duplicate_key: str | None = None
    status: LeadStatus = LeadStatus.new
    tags: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    last_verified: str | None = None
    notes: str = ""

    @field_validator("company_name")
    @classmethod
    def company_name_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("company_name darf nicht leer sein")
        return value.strip()


class EmailDraft(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    lead_id: str | None = None
    to_email: EmailStr | None = None
    subject: str
    body: str
    language: str = "de"
    approved: bool = False
    sent: bool = False
    created_at: str = Field(default_factory=now_iso)


class IngestResult(BaseModel):
    action: str
    lead: Lead
    matched_existing_id: str | None = None
    warnings: list[str] = Field(default_factory=list)
    changed_fields: list[str] = Field(default_factory=list)


class CommandResult(BaseModel):
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
