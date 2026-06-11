from __future__ import annotations

import pandas as pd
import streamlit as st

from app.agents.chef_agent import ChefAgent
from app.core.classifier import all_categories_text
from app.storage.factory import get_repository

st.set_page_config(page_title="DR Money Bot Dashboard", layout="wide")
repo = get_repository()
agent = ChefAgent(repo)

st.title("DR Money Bot – Multi-Agent Investment Dashboard")
st.caption("Dashboard für Befehle, Leads, Datenqualität, Dublettenprüfung und E-Mail-Entwürfe")

with st.sidebar:
    st.header("Befehl ausführen")
    command = st.text_area("Befehl", value="/suche windräder spanien projektfinanzierung", height=100)
    run = st.button("Befehl starten", type="primary")
    st.divider()
    st.write("Beispiele:")
    st.code("/suche private equity deutschland nachfolge\n/suche teure maschinen schweiz\n/lead ABC GmbH | https://abc.ch | info@abc.ch | +41 41 123 | Maschinenbau | Schweiz")

if run:
    raw = command.strip()
    if raw.startswith("/suche"):
        result = agent.run_search(raw.replace("/suche", "", 1).strip())
        st.success(result.message)
        if result.payload.get("warnings"):
            st.warning("Hinweise: " + "; ".join(result.payload["warnings"][:5]))
    elif raw.startswith("/lead"):
        parts = [p.strip() for p in raw.replace("/lead", "", 1).split("|")]
        while len(parts) < 6:
            parts.append(None)
        lead = agent.save_manual_lead(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5] or "unbekannt")
        st.success(f"Lead gespeichert/geprüft: {lead.company_name} | Qualität {lead.quality_score}%")
    elif raw.startswith("/mail"):
        st.info(agent.create_email_draft_for_latest_task())
    elif raw.startswith("/status"):
        st.info(agent.database_summary())
    else:
        st.error("Unbekannter Dashboard-Befehl. Nutze /suche, /lead, /mail oder /status.")

st.subheader("Status")
st.info(agent.database_summary())

leads = repo.list_leads()
tasks = repo.list_tasks()
drafts = repo.list_email_drafts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Leads", len(leads))
c2.metric("Suchaufträge", len(tasks))
c3.metric("E-Mail-Entwürfe", len(drafts))
c4.metric("Ø Qualität", round(sum(l.quality_score for l in leads) / len(leads), 1) if leads else 0)

st.subheader("Kategorien")
st.write(all_categories_text())

st.subheader("Leads")
if leads:
    df = pd.DataFrame([l.model_dump(mode="json") for l in leads])
    cols = ["company_name", "country", "category", "investment_type", "activity", "website", "contact_email", "phone", "ceo", "address", "quality_score", "investment_score", "duplicate_key", "status"]
    st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)
    st.download_button("Leads als CSV exportieren", df.to_csv(index=False).encode("utf-8"), "dr_money_leads.csv", "text/csv")
else:
    st.write("Noch keine Leads vorhanden.")

st.subheader("E-Mail-Entwürfe")
if drafts:
    st.dataframe(pd.DataFrame([d.model_dump(mode="json") for d in drafts]), use_container_width=True)
else:
    st.write("Noch keine E-Mail-Entwürfe vorhanden.")
