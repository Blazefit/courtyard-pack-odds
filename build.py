"""Inject odds + price data into index.html template -> docs/index.html for GitHub Pages."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
tpl = (ROOT / 'index.html').read_text(encoding='utf-8')

odds = json.loads((ROOT / 'odds_data.json').read_text(encoding='utf-8'))
price = json.loads((ROOT / 'price_data.json').read_text(encoding='utf-8'))
pulled = sys.argv[1] if len(sys.argv) > 1 else 'July 11, 2026'

out = tpl.replace('/*__ODDS__*/[]', json.dumps(odds, separators=(',', ':')))
out = out.replace('/*__PRICE__*/[]', json.dumps(price, separators=(',', ':')))
out = out.replace('__PULLED__', pulled)

dest = ROOT / 'docs'
dest.mkdir(exist_ok=True)
(dest / 'index.html').write_text(out, encoding='utf-8')
print('wrote', dest / 'index.html', len(out), 'bytes')
