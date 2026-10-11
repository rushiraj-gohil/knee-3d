"""Build a single self-contained index.html (phone layout, gzip'd data embedded as base64) from site/ -> single/index.html"""
import base64, json, os, sys
site = sys.argv[1] if len(sys.argv) > 1 else 'site'
out = sys.argv[2] if len(sys.argv) > 2 else 'single'
emb = {'meta': json.load(open(f'{site}/data/meta.json'))}
for k in ('bones', 'pd', 'pdfs'):
    emb[k] = base64.b64encode(open(f'{site}/data/{k}.bin.gz', 'rb').read()).decode()
html = open(f'{site}/index.html').read()
html = html.replace('<script>\nconst $=', '<script>window.EMBED=' + json.dumps(emb) + ';</script>\n<script>\nconst $=', 1)
assert 'window.EMBED' in html
os.makedirs(out, exist_ok=True)
open(f'{out}/index.html', 'w').write(html)
print('wrote', f'{out}/index.html', round(len(html)/1e6, 1), 'MB')
