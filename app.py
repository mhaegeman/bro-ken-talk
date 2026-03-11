#!/usr/bin/env python3
"""
bro-ken-talk — Streamlit web app.
Deploys free on Streamlit Community Cloud (share.streamlit.io).
"""

import os
from datetime import date

import anthropic
import streamlit as st

from recap import SYSTEM_PROMPT, USER_PROMPT

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


def generate_recap():
    """Generator that streams text chunks from Claude as they arrive."""
    today = date.today().strftime("%B %d, %Y")
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT.format(today=today)}],
        tools=[{
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": 12,
            "user_location": {
                "type": "approximate",
                "city": "Copenhagen",
                "region": "Capital Region",
                "country": "DK",
                "timezone": "Europe/Copenhagen"
            }
        }]
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                yield event.delta.text


if st.button("Get today's bro news 🍺", type="primary"):
    with st.spinner("Searching the web... (~30 seconds)"):
        st.write_stream(generate_recap())
