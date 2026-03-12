#!/usr/bin/env python3
"""
bro-ken-talk — Streamlit web app.
Deploys free on Streamlit Community Cloud (share.streamlit.io).
"""

import os
from datetime import date

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

st.set_page_config(page_title="bro-ken-talk 🍺", page_icon="🍺", layout="centered")
st.title("🍺 bro-ken-talk")
st.caption("Your daily office survival briefing — Copenhagen edition")

# Resolve API key: Streamlit Cloud secrets → env var
api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
if not api_key:
    st.error(
        "No ANTHROPIC_API_KEY found. "
        "Add it to Streamlit Cloud secrets or set the environment variable."
    )
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

today_key = date.today().isoformat()

# Sidebar: history browser
with st.sidebar:
    st.header("📅 History")
    cached_dates = list_cached_dates()
    if cached_dates:
        selected = st.selectbox(
            "View a past day",
            cached_dates,
            format_func=lambda d: f"{d} (today)" if d == today_key else d,
        )
    else:
        selected = None
        st.caption("No history yet — fetch today's recap first!")


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


# Main area
if selected and selected != today_key:
    # Viewing a historical day
    st.subheader(f"Recap for {selected}")
    st.markdown(load_cached(selected))
else:
    # Today's view
    cached_today = load_cached(today_key)
    if st.button("Get today's bro news 🍺", type="primary"):
        if cached_today:
            st.info("Showing cached results from earlier today — no API call needed.")
            st.markdown(cached_today)
        else:
            with st.spinner("Searching the web... (~30 seconds)"):
                result = st.write_stream(generate_recap())
            save_cached(today_key, result)
