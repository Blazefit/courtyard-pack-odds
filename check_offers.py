"""Check live offers on bestcards' Courtyard assets.

Usage: python check_offers.py [asset_id ...]
With no args, checks the tracked asset IDs below (competition cards + known personal cards).
"""
import json
import sys
import urllib.request

TRACKED = {
    # competition cards
    'a85c5329f169e5ceaa59881690faff54ed4b26b8e61e017395c2b174ee74fffd': 'Kyros EB01-040 CGC 10 [COMPETITION]',
    # personal collection (seen 2026-07-11)
    'f303b65bbd71bacee381f70f220b966868be3f60067e25c628c3f52c91ff5f98': 'Trey Murphy III Silver PSA 9',
    '4080fa9abe86e6a2066fda0474c348e224bb7b0a49d87624a2eb0d532cceadf6': 'Kadabra 1st Ed Shadowless PSA 9',
    'a8e48a8035646625069330c59084011c0e5fb7ff9cc0efcd6440e667c8cfa9c8': 'Slowpoke 1st Ed CGC 8',
}


def fetch(asset_id):
    req = urllib.request.Request(
        f'https://api.courtyard.io/index/asset/{asset_id}',
        headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def report(asset_id, label=None):
    d = fetch(asset_id)
    title = label or d.get('title') or asset_id[:12]
    fmv = d.get('fmv_estimate_usd')
    lst = d.get('listing_data') or []
    listed = lst[0]['price']['amount']['usd'] if lst else None
    exp = (lst[0].get('expiration') or '')[:10] if lst else ''
    print(f'== {title}')
    print(f'   FMV ${fmv} | listed: ' + (f'${listed} (expires {exp})' if listed else 'NOT LISTED')
          + f' | buyback-mark ~${round((fmv or 0) * 0.846, 2)}')
    offers = d.get('offer_data') or []
    if not offers:
        print('   no offers')
    for o in sorted(offers, key=lambda x: -x['price']['amount']['usd']):
        amt = o['price']['amount']['usd']
        oexp = (o.get('expiration') or '')[:10]
        pct_list = f' = {amt/listed*100:.0f}% of list' if listed else ''
        pct_fmv = f', {amt/fmv*100:.0f}% of FMV' if fmv else ''
        print(f'   offer ${amt} (expires {oexp}){pct_list}{pct_fmv}')


if __name__ == '__main__':
    ids = sys.argv[1:] or list(TRACKED)
    for aid in ids:
        try:
            report(aid, TRACKED.get(aid))
        except Exception as e:
            print(f'== {aid[:12]}... ERROR: {e}')
