"""Cut the axial (rows 1-3) and coronal (rows 4-6) series from page 1 into volumes, plus copies of the sagittal ones. -> vols.npz"""
import numpy as np, json, base64; from PIL import Image
a = np.asarray(Image.open('raw_p1.png').convert('L')).astype(np.float32)
W, H = a.shape[1]/6, a.shape[0]/6
vols = {}
for name, r0 in (('ax', 0), ('cor', 3)):
    sl = []
    for idx in range(1, 17):
        r = r0 + idx//6; c = idx % 6
        t = a[int(r*H)+2:int((r+1)*H)-2, int(c*W)+2:int((c+1)*W)-2].copy(); h, w = t.shape
        t[:int(h*.03), int(w*.4):int(w*.6)] = 0; t[int(h*.45):int(h*.55), :int(w*.08)] = 0
        sl.append(np.asarray(Image.fromarray(t.astype(np.uint8)).resize((256, 312), Image.LANCZOS)))
    v = np.stack(sl).astype(np.float32); lo, hi = np.percentile(v, 1), np.percentile(v, 99.7)
    vols[name] = ((v-lo)/(hi-lo)).clip(0, 1)
j = json.load(open('vol.json'))
vols['sagfs'] = np.frombuffer(base64.b64decode(j['pdfs']), np.uint8).reshape(16, 312, 256)/255.
vols['sagpd'] = np.frombuffer(base64.b64decode(j['pd']), np.uint8).reshape(16, 312, 256)/255.
np.savez('vols.npz', **vols); print('wrote vols.npz')
