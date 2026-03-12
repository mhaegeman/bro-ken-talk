#!/usr/bin/env python3
"""
bro-ken-talk — Your daily bro news survival guide.
Searches the web for sports, entertainment, drinks, and trending topics
that your male colleagues in Copenhagen are buzzing about.
"""

import json
import os
import sys
from pathlib import Path

import anthropic

_CACHE_FILE = Path(__file__).parent / "cache.json"
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
WEB_SEARCH_BETA = "web-search-2025-03-05"
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
    "user_location": {
        "type": "approximate",
        "city": "Copenhagen",
        "region": "Capital Region",
        "country": "DK",
        "timezone": "Europe/Copenhagen",
    },
}


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        return json.loads(_CACHE_FILE.read_text())
    return {}


def load_cached(date_key: str) -> str | None:
    """Return cached recap text for YYYY-MM-DD, or None."""
    return _load_cache().get(date_key)


def save_cached(date_key: str, text: str):
    """Append/update date_key in cache.json (all history preserved)."""
    data = _load_cache()
    data[date_key] = text
    _CACHE_FILE.write_text(json.dumps(data, indent=2))


def list_cached_dates() -> list:
    """Return all cached dates sorted newest-first."""
    return sorted(_load_cache().keys(), reverse=True)

SYSTEM_PROMPT = """You are a brilliant, witty friend helping a woman catch up on what her male
colleagues in Copenhagen are talking about. She needs to be able to hold her own in office
small talk about sports, entertainment, drinks, and trending bro culture topics.

Your job is to give her ready-to-use conversation starters — NOT a boring news ticker.
Every single item should be phrased as something she can actually say out loud at the coffee
machine or in a meeting, e.g.:
- "Did you see that [X] happened last night? Crazy result."
- "Apparently everyone's going crazy about [Y] right now."
- "I heard [Z] just dropped — people are losing their minds."

Output format:
- Use casual section headers (emoji + bold label)
- 3–5 items per section
- Each item: one punchy sentence that sounds natural in conversation
- End with a **WILDCARD** section — one weird/viral/unexpected thing that's trending

Tone: friendly, slightly cheeky, like a mate giving you a quick briefing before a meeting.
Keep it light and fun. No bullet-point news anchor vibes."""

USER_PROMPT = """Search the web for what men in Copenhagen, Denmark are talking about RIGHT NOW (today is {today}).

Cover ALL of these categories with fresh, current information:

🏆 SPORTS (Danish Superliga latest results especially FCK and Brøndby, UEFA Champions League,
English Premier League standings/results, Formula 1 latest race/standings, NBA highlights,
Danish handball news, cycling news if any Danish riders in the news)

🎮 ENTERTAINMENT (most hyped video game right now, top Netflix/streaming show everyone's
watching, music release or concert people are excited about)

🍺 DRINKS & NIGHTLIFE (any trending Copenhagen bar or club, craft beer or spirits news,
what people are drinking right now)

🔥 TRENDING (anything viral or buzzy among men in Denmark — tech gadgets, memes,
controversies, whatever is generating pub conversation right now)

🎲 WILDCARD (one surprising or unexpected story that will make her sound plugged-in)

Search for the most current information and give me conversation-ready talking points
for each category."""


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Get your key at: https://console.anthropic.com/")
        sys.exit(1)

    from datetime import date
    today = date.today().strftime("%B %d, %Y")
    today_key = date.today().isoformat()

    cached = load_cached(today_key)
    if cached:
        print("(Serving cached result for today)\n")
        print(cached)
        return

    client = anthropic.Anthropic(api_key=api_key)

    print("🍺 Fetching today's bro news... (this takes ~30 seconds)\n")

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        betas=[WEB_SEARCH_BETA],
        messages=[{
            "role": "user",
            "content": USER_PROMPT.format(today=today)
        }],
        tools=[WEB_SEARCH_TOOL],
    )

    # Extract only the final text output — skip internal tool use blocks
    output_parts = [
        block.text
        for block in response.content
        if block.type == "text"
    ]

    print("=" * 60)
    print("  BRO-KEN TALK — Your Office Survival Briefing")
    print(f"  {today}")
    print("=" * 60)
    print()
    full_text = "\n".join(output_parts)
    print(full_text)
    print()

    save_cached(today_key, full_text)

    # Show search count if available
    searches_used = getattr(
        getattr(response.usage, "server_tool_use", None),
        "web_search_requests",
        None
    )
    if searches_used is not None:
        print(f"(Powered by {searches_used} web searches)")


if __name__ == "__main__":
    main()
