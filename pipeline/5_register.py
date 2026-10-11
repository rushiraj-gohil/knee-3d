import numpy as np, itertools, sys
from scipy import ndimage as ndi, optimize
V=np.load('vols.npz'); S=ndi.gaussian_filter(V['sagfs'],(0.5,1,1))
def coords(kind,p,step=3):
    M=V[kind]; n,h,w=M.shape
    j,v,u=np.meshgrid(np.arange(n),np.arange(0,h,step),np.arange(0,w,step),indexing='ij')
    vals=M[:, ::step, ::step]
    if kind=='cor':
        a0,da,s,by,zc,kz=p; x=a0+j*da; y=s*v+by; z=zc+(u-128)*kz; 
    else:  # axial: v=AP (top=anterior), u=LR
        s0,ds,s,bx,zc,kz=p; y=s0+j*ds; x=s*v+bx; z=zc+(u-128)*kz
    return np.stack([z,y,x]),vals
def score(kind,p,step=3):
    c,vals=coords(kind,p,step)
    ok=(c[0]>=0)&(c[0]<=15)&(c[1]>=0)&(c[1]<=311)&(c[2]>=0)&(c[2]<=255)&(vals>0.02)
    if ok.sum()<3000: return 1.0
    s=ndi.map_coordinates(S,c[:,ok],order=1); t=vals[ok]
    s=s-s.mean();t=t-t.mean(); return -float((s*t).sum()/np.sqrt((s*s).sum()*(t*t).sum()))
def fit(kind,starts):
    res=[]
    for st in starts:
        r=score(kind,st,6); res.append((r,st))
    res.sort(key=lambda r:r[0]); best=[]
    for r,st in res[:8]:
        o=optimize.minimize(lambda p:score(kind,p,4),st,method='Powell',options={'maxiter':4000,'xtol':1e-3,'ftol':1e-5})
        best.append((o.fun,list(np.round(o.x,4))))
    best.sort(key=lambda b:b[0]); return best
kind=sys.argv[1]
if kind=='cor':
    starts=[[a0,da,s,by,7.5,kz] for a0 in (0,20,40,60) for da in (8,11,14) for s in (0.9,1.0,1.1) for by in (-40,0,40) for kz in (-.13,-.09,.09,.13)]
else:
    starts=[[s0,ds,s,bx,7.5,kz] for s0 in (0,30,60) for ds in (8,11,14) for s in (0.9,1.0,1.1) for bx in (-40,0,40) for kz in (-.13,-.09,.09,.13)]
b=fit(kind,starts)
for x in b[:4]: print(x)
np.save(f'reg_{kind}.npy',np.array(b[0][1]))
