# bro-ken-talk 🍺

Stay up to date on what the guys at work are talking about.

Searches the web for today's sports results, trending entertainment, Copenhagen bar news,
and whatever else men are buzzing about — then gives you ready-to-use conversation starters.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

> **Note:** Web search must be enabled for your API key.
> Check: https://console.anthropic.com/settings/privacy

## Run

```bash
python recap.py
```

Takes ~30 seconds while it searches the web. Outputs talking points you can drop into
office small talk today.

## What you get

- **Sports** — Danish Superliga, Champions League, Premier League, F1, NBA, handball
- **Entertainment** — Video games, streaming shows, music
- **Drinks & Nightlife** — Copenhagen bar news, craft beer, what's trending
- **Trending** — Viral stuff, tech gadgets, pub conversation topics
- **Wildcard** — One unexpected thing to make you sound plugged-in
