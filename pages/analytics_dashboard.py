"""Analytics dashboard page for the Streamlit app."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models.database import Application, SessionLocal
from services.analytics import get_application_stats, get_llm_stats, get_top_companies


st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("Analytics Dashboard")
st.caption("Track application volume, response rate, and pipeline usage over time.")

stats = get_application_stats(30)
llm_stats = get_llm_stats(30)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Applications (30d)", stats["total_applications"])
col2.metric("Responses", stats["responses"])
col3.metric("Response Rate", f"{stats['response_rate']}%")
col4.metric("Avg Match Score", f"{stats['average_match_score']}%")

col5, col6 = st.columns(2)
col5.metric("LLM Runs (30d)", llm_stats["executions"])
col6.metric("Avg Pipeline Time", f"{llm_stats['average_execution_time_ms']} ms")

cutoff_date = datetime.utcnow() - timedelta(days=30)
with SessionLocal() as db:
    rows = (
        db.query(Application.created_at)
        .filter(Application.created_at >= cutoff_date)
        .order_by(Application.created_at)
        .all()
    )

apps = pd.DataFrame(rows, columns=["created_at"])
if not apps.empty:
    apps["date"] = pd.to_datetime(apps["created_at"]).dt.date
    apps = apps.groupby("date").size().reset_index(name="count")

if not apps.empty:
    fig = px.line(apps, x="date", y="count", title="Applications Over Time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No application data found yet. Submit a few applications to populate this dashboard.")

top_companies = get_top_companies(10)
if top_companies:
    df = pd.DataFrame(top_companies)
    fig = px.bar(df, x="company", y="count", title="Top Companies Applied To")
    st.plotly_chart(fig, use_container_width=True)
