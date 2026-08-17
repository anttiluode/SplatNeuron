"""Gate 10 v2: frozen MNIST scale experiment, plumbing-fixed.

Scientific settings are unchanged from gate10_mnist_scale.py:
D=784, 8 complex Gabor receivers -> 16 real values, 32 geometry scalars,
6000/1000/5000 train/val/test examples, 80 epochs, LR=.02, batch=256,
seeds 9100/9101.  The only substantive code fix is cloning meshgrid buffers so
PyTorch can restore the validation-best state_dict safely.
"""
from __future__ import annotations

import argparse, copy, math, time
from dataclasses import dataclass
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn import functional as F
from torchvision.datasets import MNIST

N=8; M=16; D=784; C=10; BATCH=256; EPOCHS=80; LR=.02
TRAIN_N=6000; VAL_N=1000; TEST_N=5000; SEEDS=(9100,9101)
torch.set_num_threads(2)

class Gabor28(nn.Module):
    def __init__(self, raw, trainable):
        super().__init__(); self.raw=nn.Parameter(raw.clone(),requires_grad=trainable)
        yy,xx=torch.meshgrid(torch.linspace(0,1,28),torch.linspace(0,1,28),indexing='ij')
        self.register_buffer('xx',xx.clone()); self.register_buffer('yy',yy.clone())
    def filt(self):
        s=torch.sigmoid(self.raw); cx=.05+.90*s[:,0]; cy=.05+.90*s[:,1]
        freq=.7+3.3*s[:,2]; th=np.pi*s[:,3]
        dx=self.xx[None]-cx[:,None,None]; dy=self.yy[None]-cy[:,None,None]
        co=torch.cos(th)[:,None,None]; si=torch.sin(th)[:,None,None]
        xr=co*dx+si*dy; yr=-si*dx+co*dy; sig=.22
        env=torch.exp(-.5*(xr*xr+yr*yr)/(sig*sig)); ph=2*np.pi*freq[:,None,None]*xr
        re=env*torch.cos(ph); im=env*torch.sin(ph)
        re=re/(re.flatten(1).norm(dim=1)[:,None,None]+1e-8)
        im=im/(im.flatten(1).norm(dim=1)[:,None,None]+1e-8)
        return re,im
    def forward(self,x):
        re,im=self.filt(); q=x[:,0]
        return torch.cat([torch.einsum('bhw,nhw->bn',q,re),torch.einsum('bhw,nhw->bn',q,im)],1)
    @torch.no_grad()
    def matrix(self):
        re,im=self.filt(); return torch.cat([re.flatten(1),im.flatten(1)],0)

class Learned(nn.Module):
    def __init__(self,raw): super().__init__(); self.sensor=Gabor28(raw,True); self.head=nn.Linear(M,C)
    def forward(self,x): return self.head(self.sensor(x))

@dataclass
class Data:
    x:torch.Tensor; y:torch.Tensor; xv:torch.Tensor; yv:torch.Tensor; xt:torch.Tensor; yt:torch.Tensor

def data(root,download,seed):
    tr=MNIST(root,train=True,download=download); te=MNIST(root,train=False,download=download)
    xa=tr.data.numpy().astype('float32')/255.; ya=tr.targets.numpy().astype('int64')
    xb=te.data.numpy().astype('float32')/255.; yb=te.targets.numpy().astype('int64')
    keep,_=train_test_split(np.arange(len(xa)),train_size=TRAIN_N+VAL_N,random_state=seed,stratify=ya)
    a,v=train_test_split(keep,train_size=TRAIN_N,test_size=VAL_N,random_state=seed+1000,stratify=ya[keep])
    t,_=train_test_split(np.arange(len(xb)),train_size=TEST_N,random_state=seed+2000,stratify=yb)
    return Data(torch.tensor(xa[a,None]),torch.tensor(ya[a]),torch.tensor(xa[v,None]),torch.tensor(ya[v]),torch.tensor(xb[t,None]),torch.tensor(yb[t]))

def fit(model,x,y,xv,yv,xt,yt,seed):
    opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=LR); best=None; bv=-1
    for ep in range(EPOCHS):
        perm=torch.randperm(len(x),generator=torch.Generator().manual_seed(seed*1000+ep))
        model.train()
        for st in range(0,len(x),BATCH):
            ii=perm[st:st+BATCH]; opt.zero_grad(); F.cross_entropy(model(x[ii]),y[ii]).backward(); opt.step()
        if (ep+1)%5==0:
            model.eval()
            with torch.no_grad(): va=float((model(xv).argmax(1)==yv).float().mean())
            if va>bv: bv=va; best=copy.deepcopy(model.state_dict())
    model.load_state_dict(best); model.eval()
    with torch.no_grad(): return float((model(xt).argmax(1)==yt).float().mean())

def head(z,y,zv,yv,zt,yt,seed,h=None):
    torch.manual_seed(seed)
    m=nn.Linear(z.shape[1],C) if h is None else nn.Sequential(nn.Linear(z.shape[1],h),nn.Tanh(),nn.Linear(h,C))
    return fit(m,z,y,zv,yv,zt,yt,seed)

def feats(mat,d):
    with torch.no_grad():
        f=lambda x:x[:,0].flatten(1)@mat.T
        return f(d.x),f(d.xv),f(d.xt)

def dct16(n=28):
    grid=np.arange(n,dtype=float); modes={}
    for u in range(6):
      for v in range(6):
        au=math.sqrt(1/n) if u==0 else math.sqrt(2/n); av=math.sqrt(1/n) if v==0 else math.sqrt(2/n)
        modes[u,v]=np.outer(au*np.cos(np.pi*(2*grid+1)*u/(2*n)),av*np.cos(np.pi*(2*grid+1)*v/(2*n))).astype('float32').reshape(-1)
    order=[]
    for s in range(10):
        q=[(u,s-u) for u in range(6) if 0<=s-u<6]
        if s%2==0:q.reverse()
        order+=q
        if len(order)>=M:break
    return np.stack([modes[p] for p in order[:M]])

def one(root,download,seed):
    d=data(root,download,seed); raw=torch.randn(N,4,generator=torch.Generator().manual_seed(100000+seed))*.7
    torch.manual_seed(200000+seed); lm=Learned(raw); t0=time.perf_counter()
    la=fit(lm,d.x,d.y,d.xv,d.yv,d.xt,d.yt,seed); secs=time.perf_counter()-t0
    fs=Gabor28(raw,False); zg,zgv,zgt=feats(fs.matrix(),d)
    h7=head(zg,d.y,zgv,d.yv,zgt,d.yt,seed+7,7); h48=head(zg,d.y,zgv,d.yv,zgt,d.yt,seed+48,48)
    x=d.x[:,0].flatten(1).numpy(); xv=d.xv[:,0].flatten(1).numpy(); xt=d.xt[:,0].flatten(1).numpy()
    p=PCA(n_components=M,svd_solver='randomized',random_state=seed); zp=torch.tensor(p.fit_transform(x),dtype=torch.float32); zpv=torch.tensor(p.transform(xv),dtype=torch.float32); zpt=torch.tensor(p.transform(xt),dtype=torch.float32)
    pa=head(zp,d.y,zpv,d.yv,zpt,d.yt,seed+1)
    zd,zdv,zdt=feats(torch.tensor(dct16()),d); da=head(zd,d.y,zdv,d.yv,zdt,d.yt,seed+2)
    full=head(d.x[:,0].flatten(1),d.y,d.xv[:,0].flatten(1),d.yv,d.xt[:,0].flatten(1),d.yt,seed+3)
    return dict(learned=la,pca=pa,dct=da,h7=h7,h48=h48,full=full,train_s=secs)

def resources():
    dense=M*D; geom=N*4; proj=M*D; lin=proj+M*C; big=proj+M*48+48*C
    print('\nresources FP32:')
    print(f'D={D} M={M} egress={M*4}B dense_coeffs={dense} geom={geom} ratio={dense/geom:.1f}x')
    print(f'Gabor+linear state={(geom+M*C+C)*4}B PCA+mean+linear state={(dense+D+M*C+C)*4}B')
    print(f'projection={proj} MACs compact+linear={lin} fixedH48={big} ratio={big/lin:.3f}x')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.mnist-data'); ap.add_argument('--download',action='store_true'); ap.add_argument('--one-seed',action='store_true'); a=ap.parse_args()
    rows=[]
    for s in (SEEDS[:1] if a.one_seed else SEEDS):
        r=one(a.root,a.download,s); rows.append(r); print(f"seed {s}: learned={r['learned']:.4f} PCA={r['pca']:.4f} DCT={r['dct']:.4f} fixedH7={r['h7']:.4f} fixedH48={r['h48']:.4f} full={r['full']:.4f} train_s={r['train_s']:.1f}")
    print('\nmeans:')
    for k in ('learned','pca','dct','h7','h48','full'):print(f'{k:<10}{np.mean([r[k] for r in rows]):.4f}')
    resources()
if __name__=='__main__':main()
