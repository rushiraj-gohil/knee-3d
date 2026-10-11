import numpy as np
from scipy import ndimage as ndi
from skimage import filters, segmentation, morphology, measure
from PIL import Image
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'5_register.py')).read().split("kind=sys.argv")[0])
M=np.load('seg.npz'); B=['femur','tibia','patella']
Ms={b:ndi.gaussian_filter(M[b].astype(np.float32),(0.7,1,1)) for b in B}
out={}
for kind in ('cor','ax'):
    p=np.load(f'reg_{kind}.npy'); c,vals=coords(kind,p,1); n,h,w=vals.shape
    inside=(c[0]>=-0.5)&(c[0]<=15.5)
    P={b:ndi.map_coordinates(Ms[b],c.reshape(3,-1),order=1,cval=0).reshape(vals.shape) for b in B}
    lab=np.zeros(vals.shape,np.uint8)
    for j in range(n):
        im=filters.gaussian(vals[j],1.0); g=filters.sobel(im)
        mk=np.zeros((h,w),np.int32)
        for k,b in enumerate(B,1):
            core=morphology.binary_erosion(P[b][j]>0.6,morphology.disk(4))
            mk[core]=k
        anyb=sum(P[b][j] for b in B)
        bg=(inside[j]&(ndi.distance_transform_edt(anyb<0.5)>7))|(im<0.04)|(im>0.6)
        bg&=mk==0
        mk[bg]=4
        if (mk[(mk>0)&(mk<4)]).size==0: continue
        ws=segmentation.watershed(g,mk)
        for k in (1,2,3):
            r=ws==k; r=morphology.binary_opening(r,morphology.disk(2)); r=ndi.binary_fill_holes(r)
            lab[j][r]=k
    out[kind]=lab
    # preview
    tiles=[]
    for j in range(0,16,2):
        rgb=np.stack([vals[j]]*3,-1)*.8
        for k,col in zip((1,2,3),[(1,.3,.3),(.3,1,.3),(.3,.6,1)]):
            m=lab[j]==k; e=m^morphology.binary_erosion(m,morphology.disk(1)); rgb[e]=col
        tiles.append(rgb)
    Image.fromarray((np.hstack(tiles)*255).astype(np.uint8)).save(f'seg2_{kind}.png')
np.savez('seg2.npz',**out)
