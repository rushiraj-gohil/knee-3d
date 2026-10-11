import numpy as np, json, base64
from scipy import ndimage as ndi
from skimage import measure
V=np.load('vols.npz'); M=np.load('seg.npz'); L=np.load('seg2.npz')
pc=np.load('reg_cor.npy'); pa=np.load('reg_ax.npy')
a0,da,sc,by,zcc,kzc=pc; s0,ds,sa,bx,zca,kza=pa
B=['femur','tibia','patella']
NX,NY,NU=112,136,112   # AP, SI, LR
x=np.linspace(0,255,NX); y=np.linspace(0,311,NY); u=np.linspace(0,255,NU)
Y,X,U=np.meshgrid(y,x,u,indexing='ij')   # grid order (y,x,u)
zs=zcc+(U-128)*kzc                          # sagittal slice coord
jc=(X-a0)/da; vc=(Y-by)/sc                  # coronal
ja=(Y-s0)/ds; va=(X-bx)/sa; ua=128+(zs-zca)/kza  # axial
cov_s=(zs>=-0.5)&(zs<=15.5); cov_c=(jc>=-0.5)&(jc<=15.5); cov_a=(ja>=-0.5)&(ja<=15.5)
def smp(vol,c0,c1,c2): return ndi.map_coordinates(vol,np.stack([c0.ravel(),c1.ravel(),c2.ravel()]),order=1,mode='nearest').reshape(c0.shape)
res=[];inten_num=np.zeros(Y.shape);inten_den=np.zeros(Y.shape)
for k,b in enumerate(B,1):
    ps=smp(ndi.gaussian_filter(M[b].astype(np.float32),(0.6,1,1)),zs,Y,X)
    pcor=smp(ndi.gaussian_filter((L['cor']==k).astype(np.float32),(0.6,1.5,1.5)),jc,vc,U)
    pax=smp(ndi.gaussian_filter((L['ax']==k).astype(np.float32),(0.6,1.5,1.5)),ja,va,ua)
    num=ps*cov_s+pcor*cov_c+pax*cov_a; den=cov_s*1.+cov_c+cov_a
    P=np.where(den>0,num/np.maximum(den,1),0)
    m=P>0.44
    lab=measure.label(m); 
    if lab.max(): m=lab==np.bincount(lab.ravel()[lab.ravel()>0]).argmax()
    m=ndi.binary_fill_holes(m)
    res.append(ndi.gaussian_filter(m.astype(np.float32),1.4))
    print(b,'voxels',int(m.sum()),'sag-only',int((m&cov_s&~cov_c&~cov_a).sum()),'outside sag',int((m&~cov_s).sum()))
for vol,cov,c in ((V['sagfs'],cov_s,(zs,Y,X)),(V['cor'],cov_c,(jc,vc,U)),(V['ax'],cov_a,(ja,va,ua))):
    inten_num+=smp(vol,*c)*cov; inten_den+=cov
I=np.where(inten_den>0,inten_num/np.maximum(inten_den,1),0)
rgba=np.stack(res+[I],-1)  # (y,x,u,4)
# texture order: width=AP(x), height=SI(y), depth=LR(u) -> array [u][y][x]
tex=np.transpose(rgba,(2,0,1,3))
j=json.load(open('vol.json'))
j['bones']=base64.b64encode((tex.clip(0,1)*255).astype(np.uint8).tobytes()).decode()
j['bw'],j['bh'],j['bd']=NX,NY,NU
j['boxB']=[256/312,1,256*sc/312]; j['boxT']=[256/312,1,16*sc/abs(kzc)/312]
json.dump(j,open('vol.json','w'))
np.save('fused.npy',tex)
print('box',j['boxB'],j['boxT'])
