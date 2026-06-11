from app.core.models import Lead
from app.storage.factory import get_repository

repo = get_repository()
lead = Lead(
    company_name="DR Money Bot Test Lead",
    website="https://example.com",
    country="Schweiz",
    city="Zug",
    notes="Automatischer Verbindungstest aus dem Bot."
)
repo.upsert_lead(lead)
print("OK: Supabase-Verbindung funktioniert. Test-Lead wurde gespeichert.")
