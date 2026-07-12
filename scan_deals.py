"""Scan Courtyard marketplace for underpriced listings (deal arbitrage).

Uses Courtyard's public Algolia search (same backend as their Best Deals tab).
Key economics under mark-to-bid scoring: instant buyback pays 84.6% of FMV, so any
listing priced below 84.6% of estimated value has a positive GUARANTEED spread
(buy -> instant buyback), and bigger upside if flipped at FMV on the 0%-fee market.

Usage:
  python scan_deals.py                    # graded cards, all categories, max $300
  python scan_deals.py --cat "One Piece"  # one category
  python scan_deals.py --max 100          # price ceiling
"""
import argparse
import json
import urllib.request

APP = 'Y8TL3M06QA'
KEY = '3b3ed18284ca0baee9a496aea5f093d6'  # public search-only key from courtyard.io
URL = f'https://y8tl3m06qa-dsn.algolia.net/1/indexes/marketplace_prod_best_deals/query'
BUYBACK = 0.846


def query_page(page, hits=1000):
    body = json.dumps({'query': '', 'hitsPerPage': hits, 'page': page}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        'x-algolia-api-key': KEY, 'x-algolia-application-id': APP,
        'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)['hits']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cat', default=None, help='substring, e.g. "One Piece", "Pok"')
    ap.add_argument('--coll', default=None, help='substring, e.g. "Graded Cards", "Booster"')
    ap.add_argument('--max', type=float, default=300, help='max listing price USD')
    ap.add_argument('--minspread', type=float, default=0, help='min guaranteed spread $')
    ap.add_argument('--pages', type=int, default=3, help='pages of 1000 to scan (deal-sorted)')
    args = ap.parse_args()

    hits = []
    for p in range(args.pages):
        batch = query_page(p)
        hits.extend(batch)
        if not batch or (batch[-1].get('dealScore') or 0) < 5:
            break  # deal-sorted index: nothing meaningful further down

    rows = []
    for h in hits:
        conf = str(h.get('estimatedValueConfidence'))
        if conf != 'high':
            continue
        if args.cat and args.cat.lower() not in str((h.get('metadata') or {}).get('Category', '')).lower():
            continue
        if args.coll and not str(h.get('collection', '')).lower().startswith(args.coll.lower()):
            continue
        p_ = (h.get('price') or {}).get('amountUsd')
        if not p_ or p_ > args.max:
            continue
        price = (h.get('price') or {}).get('amountUsd')
        est = h.get('estimatedValueUsd')
        if not price or not est:
            continue
        bid = est * BUYBACK
        rows.append({
            'title': h['title'][:78],
            'cat': (h.get('metadata') or {}).get('Category', '?'),
            'price': price,
            'est': est,
            'deal': h.get('dealScore'),
            'bid': round(bid, 2),
            'spread': round(bid - price, 2),          # guaranteed via instant buyback
            'flip': round(est - price, 2),            # if sold at FMV, 0% fees
            'id': h['objectID'],
        })
    rows.sort(key=lambda r: -r['spread'])
    print(f"{'PRICE':>7} {'EST':>8} {'DEAL%':>6} {'GTD SPREAD':>10} {'FLIP@FMV':>9}  TITLE [CATEGORY]")
    for r in rows[:30]:
        if r['spread'] < args.minspread:
            continue
        print(f"${r['price']:>6} ${r['est']:>7} {r['deal']:>5.0f}% "
              f"${r['spread']:>9} ${r['flip']:>8}  {r['title']} [{r['cat']}]")
        print(f"{'':34} https://courtyard.io/asset/{r['id']}")


if __name__ == '__main__':
    main()
