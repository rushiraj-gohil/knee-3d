"""Cut the two 18-tile sagittal series from page 3 into volumes (PD-FS = rows 1-3, PD = rows 4-6).
First/last tile of each series are dropped (they carry patient-identifying text); orientation labels masked. -> vol.json"""
import numpy as np, base64, json; from PIL import Image
a = np.asarray(Image.open('raw_p3.png').convert('L')).astype(np.float32)
W, H = a.shape[1]/6, a.shape[0]/6
TW, TH = 256, 312
out = {}
for name, r0 in (('pdfs', 0), ('pd', 3)):
    sl = []
    for idx in range(1, 17):
        r = r0 + idx//6; c = idx % 6
        t = a[int(r*H)+2:int((r+1)*H)-2, int(c*W)+2:int((c+1)*W)-2].copy(); h, w = t.shape
        t[:int(h*.03), int(w*.4):int(w*.6)] = 0; t[int(h*.45):int(h*.55), :int(w*.06)] = 0
        sl.append(np.asarray(Image.fromarray(t.clip(0, 255).astype(np.uint8)).resize((TW, TH), Image.LANCZOS)))
    v = np.stack(sl).astype(np.float32)
    lo, hi = np.percentile(v, 1), np.percentile(v, 99.7)
    out[name] = base64.b64encode((((v-lo)/(hi-lo)).clip(0, 1)*255).astype(np.uint8).tobytes()).decode()
json.dump({'w': TW, 'h': TH, 'd': 16, **out}, open('vol.json', 'w'))
print('wrote vol.json')
