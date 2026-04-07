#!/usr/bin/env python3
"""
bro-ken-talk — Streamlit web app.
Deploys free on Streamlit Community Cloud (share.streamlit.io).
"""

import os
from datetime import date, datetime

import anthropic
import streamlit as st

from recap import (
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    USER_PROMPT,
    WEB_SEARCH_BETA,
    WEB_SEARCH_TOOL,
    load_cached,
    save_cached,
    list_cached_dates,
)

st.set_page_config(page_title="bro-ken-talk", page_icon="🍺", layout="centered")

# ── Custom CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default Streamlit header/footer for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hero header */
    .hero {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        background: linear-gradient(135deg, #f59e0b, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero .tagline {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* Date pill */
    .date-pill {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 999px;
        padding: 0.3rem 1rem;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    /* Recap card */
    .recap-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin: 0.75rem 0;
        line-height: 1.7;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0c1222;
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>bro-ken-talk</h1>
    <div class="tagline">Your daily office survival briefing &mdash; Copenhagen edition</div>
</div>
""", unsafe_allow_html=True)

# ── API key ─────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
if not api_key:
    st.error(
        "No ANTHROPIC_API_KEY found. "
        "Add it to Streamlit Cloud secrets or set the environment variable."
    )
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

today_key = date.today().isoformat()
today_display = date.today().strftime("%A, %B %d, %Y")

# ── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### History")
    cached_dates = list_cached_dates()
    if cached_dates:
        selected = st.selectbox(
            "Browse past days",
            cached_dates,
            format_func=lambda d: (
                f"{d}  (today)" if d == today_key
                else datetime.fromisoformat(d).strftime("%a %b %d")
            ),
            label_visibility="collapsed",
        )
    else:
        selected = None
        st.caption("No history yet.")

    st.divider()
    st.caption("Powered by Claude + web search")


# ── Stream helper ───────────────────────────────────────────────────────
def generate_recap():
    """Generator that streams text chunks from Claude as they arrive."""
    today = date.today().strftime("%B %d, %Y")
    with client.messages.stream(
        model=DEFAULT_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        extra_headers={"anthropic-beta": WEB_SEARCH_BETA},
        messages=[{"role": "user", "content": USER_PROMPT.format(today=today)}],
        tools=[WEB_SEARCH_TOOL],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                yield event.delta.text


# ── Main content ────────────────────────────────────────────────────────
def render_recap(text, label):
    """Display recap inside a styled card."""
    st.markdown(f'<div class="date-pill">{label}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="recap-card">{st.session_state.get("_noop", "")}</div>',
        unsafe_allow_html=True,
    ) if False else None  # placeholder; real render below
    st.markdown(text)


if selected and selected != today_key:
    label = datetime.fromisoformat(selected).strftime("%A, %B %d, %Y")
    st.markdown(f'<div class="date-pill">{label}</div>', unsafe_allow_html=True)
    st.markdown(load_cached(selected))
else:
    st.markdown(
        f'<div class="date-pill">{today_display}</div>',
        unsafe_allow_html=True,
    )

    cached_today = load_cached(today_key)

    if cached_today:
        st.markdown(cached_today)
        st.button("Refresh", type="secondary", disabled=True,
                  help="Already fetched today's briefing")
    else:
        if st.button("Get today's briefing", type="primary", use_container_width=True):
            with st.spinner("Searching the web..."):
                result = st.write_stream(generate_recap())
            save_cached(today_key, result)
            st.rerun()
