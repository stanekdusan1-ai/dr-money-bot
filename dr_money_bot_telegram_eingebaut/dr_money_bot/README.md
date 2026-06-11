# DR Money Bot – Professional Multi-Agent Investment Search

Ein sauber strukturierter Python-Bot für weltweite Investment-, Projekt-, Unternehmens-, Sponsoring-, Maschinen-, Energie-, Luxusgüter- und Produkt-Recherche.

## Wichtigster Grundsatz
Such-Agenten dürfen Funde sammeln, aber **nur die zentrale Datenqualitäts- und Dublettenprüfung schreibt in die Datenbank**. Dadurch bleibt die Datenbank sauber und enthält pro realem Unternehmen nur einen möglichst vollständigen Datensatz.

## Enthaltene Hauptfunktionen

- Multi-Agent-Logik für viele Branchen und Investmentarten
- Automatische Kategorie- und Investmenttyp-Erkennung
- Telegram-Befehle
- Streamlit-Dashboard mit Befehlsfeld
- Saubere Lead-Datenbank als JSON-Startversion
- Zentrale Datenqualitätsprüfung
- Dublettenlogik über Domain, E-Mail-Domain, Telefonnummer, Firmenname und Land
- Vollständige Lead-Felder: Firmenname, Tätigkeit, Website, E-Mail, Telefon, CEO, Ansprechpartner, Adresse, Land, UID/VAT, Umsatz, Mitarbeiter, Kapitalbedarf, Quellen, Score
- E-Mail-Entwürfe für Suchaufträge und Leads
- Tests für Kernlogik

## Agenten

- Private-Equity-Scout
- Projektfinanzierungs-Scout
- Hotel-Scout
- Energie-Scout: Windräder, Windparks, Solar, Biogas, Wasserstoff
- Maschinen-Scout: teure Maschinen, Industrieanlagen, Produktionsanlagen
- Fahrzeug- und Logistik-Scout
- Luxus-Scout: Yachten, Flugzeuge, Pferde, Luxusassets
- Healthcare-Scout
- Innovation-Ideen-Agent: neue lukrative Produkte, Patente, Technologien, Trends
- Sponsoring-Scout

## Telegram-Befehle

```text
/start
/hilfe
/branchen
/suche <Thema/Land/Budget>
/status
/leads
/mail
/lead Name | Website | Email | Telefon | Tätigkeit | Land
```

Beispiele:

```text
/suche windräder spanien projektfinanzierung
/suche private equity deutschland unternehmensnachfolge
/suche teure maschinen schweiz kapitalbedarf
/suche neue lukrative produkte energie europa
/lead ABC Wind GmbH | https://abc-wind.ch | info@abc-wind.ch | +41 41 123 45 67 | Windenergie-Projektentwickler | Schweiz
```

## Dashboard

Start:

```bash
streamlit run app/dashboard/streamlit_app.py
```

Im Dashboard können Befehle direkt ausgeführt werden:

- `/suche ...`
- `/lead ...`
- `/mail`
- `/status`

Außerdem zeigt das Dashboard Leads, E-Mail-Entwürfe, Qualitätswerte und CSV-Export.

## Installation lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Dann `.env` ausfüllen.

Bot starten:

```bash
python -m app.main_bot
```

Tests ausführen:

```bash
pytest -q
```

## Aktueller Recherchemodus

Der aktuelle `ResearchClient` läuft bewusst im sicheren Demo-Modus. Er erzeugt strukturierte Beispiel-Leads, damit Datenbank, Dashboard, Telegram, Dublettenprüfung und E-Mail-Entwürfe geprüft werden können.

Für echte Recherche werden später API-Provider angeschlossen:

- Firecrawl für Webseiten-Crawling
- Brave Search oder Serper für Websuche
- Handelsregister-/Firmendaten-APIs
- optional OpenAI/OpenRouter für Analyse und Klassifizierung

## Datenbankqualität

Ein Lead enthält unter anderem:

- company_name
- legal_name
- activity
- website/domain
- contact_email
- phone
- address/city/postal_code/country
- ceo/contact_person/role
- linkedin
- uid_vat
- employees/revenue
- capital_need/capital_need_text
- estimated_ticket_size
- sources
- quality_score
- investment_score
- duplicate_key
- status

## Nächster Ausbauschritt

1. Firecrawl/Serper/Brave API anschließen
2. echte Quellen speichern
3. Handelsregisterdaten ergänzen
4. Supabase als produktive Datenbank aktivieren
5. Freigabe-Workflow für E-Mail-Versand einbauen


## Supabase-Verbindung testen

Die Supabase-Verbindung ist über `.env` vorbereitet. Zum Testen im Projektordner ausführen:

```bash
python scripts/check_supabase_connection.py
```

Wenn `OK: Supabase-Verbindung funktioniert...` erscheint, wurde ein Test-Lead in der Tabelle `leads` gespeichert.
