# bro-ken-talk

Daily office-survival briefing — Copenhagen edition. Searches the web for sports,
entertainment, drinks, and trending topics men in Copenhagen are talking about,
then serves them as ready-to-use conversation starters.

## Architecture

| File | Role |
|------|------|
| `app.py` | Streamlit web UI — streaming response, sidebar history browser |
| `recap.py` | Core logic: constants, prompts, JSON cache helpers, CLI entry point |
| `cache.json` | Auto-created at runtime, gitignored — keyed by YYYY-MM-DD |

`app.py` imports everything it needs (`DEFAULT_MODEL`, `SYSTEM_PROMPT`, `USER_PROMPT`,
`WEB_SEARCH_BETA`, `WEB_SEARCH_TOOL`, cache helpers) from `recap.py`.

## Running locally

```bash
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py   # browser UI at http://localhost:8501
python recap.py        # CLI — prints recap to stdout
```

## Cost rules — always follow these

- **Model**: use `DEFAULT_MODEL` (`claude-sonnet-4-5` unless `ANTHROPIC_MODEL` env var overrides).
  Never hardcode Opus — it is ~5× more expensive and unnecessary for this task.
- **max_tokens**: keep ≤ 1500. Output is ~20 short conversational lines (~500 tokens).
- **max_uses** (web searches): keep ≤ 5 in `WEB_SEARCH_TOOL`. One search per content category
  (Sports, Entertainment, Drinks, Trending, Wildcard) is sufficient.
- **Beta header**: `betas=[WEB_SEARCH_BETA]` is required on every API call that uses the
  `web_search_20250305` tool type. Omitting it causes a 400 BadRequestError.
- **Prompts**: do not extend `SYSTEM_PROMPT` or `USER_PROMPT` — longer prompts mean more input
  tokens billed on every single call.

## Caching

- `cache.json` is keyed by ISO date (YYYY-MM-DD). A new day = a new cache key = fresh API call.
- Within the same day: cache hit → result served instantly, no API call made.
- On Streamlit Cloud, `cache.json` persists for the life of the container (hours–days).
  Container restarts reset it, but that is acceptable since they typically coincide with a new day.
- **When testing locally**: call `load_cached(date_key)` to check for existing data before
  triggering a real API call. Never run the full stack just to test UI changes.

## Do not

- Add new Python dependencies without a clear reason (`requirements.txt` is intentionally minimal).
- Increase `max_tokens`, `max_uses`, or switch to Opus without explicit justification.
- Create extra files (helpers, utils, config modules) for one-off operations.
- Add error handling for scenarios that cannot happen in normal use.
