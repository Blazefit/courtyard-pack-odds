# Courtyard.io — Pack Odds & Collection Trends

Single-page market brief answering two questions:

1. **Which Courtyard pack raffles have the best odds?** — Live odds pulled from
   Courtyard's public pack API (`api.courtyard.io/vending-machines`) for every
   in-stock pack. Every pack is tuned to ~97% expected value, so packs are ranked
   by *hit rate*: the probability the pulled item comps at or above the pack price.
2. **How has each collection moved over the last year?** — 12-month indexed price
   action (rebased July 2025 = 100) for each collection Courtyard sells: graded
   Pokémon, sports cards, One Piece, graded coins, luxury watches, and comics,
   with 3M / 6M / 12M change chips and cited sources per card.

## Layout

- `index.html` — page template (data placeholders)
- `odds_data.json` — snapshot of per-pack odds buckets, EV, buyback ratio
- `price_data.json` — per-collection monthly index series + sources
- `build.py` — injects both JSON files into the template → `docs/index.html`
- `docs/` — built page served by GitHub Pages

## Refresh

```bash
# re-pull odds snapshot, then:
python build.py "Month DD, YYYY"
git add -A && git commit -m "chore: refresh data" && git push
```

Not financial advice. Collectibles are volatile; Courtyard recomputes odds in real time.
