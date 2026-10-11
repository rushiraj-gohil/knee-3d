import json,base64,numpy as np
from skimage import filters, morphology, measure
from scipy import ndimage as ndi
from PIL import Image
j=json.load(open('vol.json'));V=np.frombuffer(base64.b64decode(j['pd']),np.uint8).reshape(16,312,256).astype(float)/255
keys={'femur':{2:(147,128),5:(128,115),8:(128,109),11:(128,128),14:(160,128)},
      'tibia':{2:(147,211),5:(133,228),8:(134,243),11:(154,224),14:(160,211)},
      'patella':{4:(58,95),7:(58,108),10:(57,100)}}
rng={'femur':range(0,16),'tibia':range(0,16),'patella':range(3,12)}
lim={'femur':14000,'tibia':12000,'patella':2500}
def seed(b,z):
    k=sorted(keys[b]);return int(np.interp(z,k,[keys[b][q][0] for q in k])),int(np.interp(z,k,[keys[b][q][1] for q in k]))
def grow(s,x,y,b,prior=None):
    for er in (2,3,4,5,6):
        for hi in (0.86,0.8,0.76):
            m=morphology.binary_erosion((s>0.45)&(s<hi),morphology.disk(er))
            lab=measure.label(m);yy,xx=np.nonzero(lab)
            if len(yy)==0: continue
            d=(yy-y)**2+(xx-x)**2;i=d.argmin()
            if d[i]>12**2: continue
            c=ndi.binary_fill_holes(morphology.binary_dilation(lab==lab[yy[i],xx[i]],morphology.disk(er)))
            if prior is not None and prior.sum()>0:
                c&=morphology.binary_dilation(prior,morphology.disk(9))
                c=morphology.binary_opening(c,morphology.disk(3))
                if c.sum()==0: continue
                L=measure.label(c);c=L==np.bincount(L.ravel()[L.ravel()>0]).argmax()
            a=c.sum();sol=measure.regionprops(c.astype(int))[0].solidity
            if 150<a<lim[b] and sol>(0.72 if (b=='tibia' and prior is not None) else 0.86): return c
    return None
out={b:np.zeros(V.shape,bool) for b in keys};log=[]
S=[filters.gaussian(V[z],1.2) for z in range(16)]
for b in keys:
    c0=8 if b!='patella' else 7
    for order in (range(c0,16),range(c0-1,-1,-1)):
        prior=None
        for z in order:
            if z not in rng[b]: continue
            c=grow(S[z],*seed(b,z),b,prior)
            if c is not None:
                if b!='femur': c&=~out['femur'][z]
                out[b][z]=c; prior=c
            log.append((b[0],z,'X' if c is None else int(c.sum())))
print(log)
for b in out:
    for z in rng[b]:
        if out[b][z].sum()==0:
            nb=[out[b][q] for q in (z-1,z+1) if 0<=q<16 and out[b][q].sum()>0]
            if len(nb)==2: out[b][z]=(nb[0].astype(float)+nb[1])/2>=0.5
np.savez('seg.npz',**out)
rows=[]
for z in range(0,16,1):
    im=np.stack([V[z]]*3,-1)*0.7
    for b,c in zip(keys,[(1,.3,.3),(.3,1,.3),(.3,.6,1)]):
        e=out[b][z]^morphology.binary_erosion(out[b][z],morphology.disk(1));im[e]=c
    rows.append(im)
g=np.vstack([np.hstack(rows[i:i+8]) for i in (0,8)])
Image.fromarray((g*255).astype(np.uint8)).save('segcheck.png')
