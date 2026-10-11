"""Embed vol.json into the viewer template -> knee_3d.html"""
s = open('viewer_template.html').read().replace('__VOL__', open('vol.json').read())
open('knee_3d.html', 'w').write(s); print('wrote knee_3d.html', round(len(s)/1e6, 1), 'MB')
