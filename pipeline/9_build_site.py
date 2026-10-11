"""Build the deployable static site from vol.json -> site/ (index.html + data/*.bin + meta.json + vercel.json).
Data is raw uint8 voxels, gzip'd (lossless) and decompressed in the browser."""
import json, base64, os, shutil, sys, gzip
here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else 'site'
j = json.load(open('vol.json'))
os.makedirs(f'{out}/data', exist_ok=True)
for k in ('bones', 'pd', 'pdfs'):
    open(f'{out}/data/{k}.bin.gz', 'wb').write(gzip.compress(base64.b64decode(j[k]), 9, mtime=0))
meta = {k: j[k] for k in ('w', 'h', 'd', 'bw', 'bh', 'bd', 'boxB', 'boxT')}
json.dump(meta, open(f'{out}/data/meta.json', 'w'))
shutil.copy(os.path.join(here, 'site_template.html'), f'{out}/index.html')
json.dump({"headers": [
    {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
    {"source": "/data/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400"}]}]},
    open(f'{out}/vercel.json', 'w'), indent=2)
print('wrote', out)
