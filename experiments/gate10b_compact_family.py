"""Gate 10b: post-hoc compact non-frequency attackers on frozen MNIST protocol.

Gate 10 observed 88.33% mean for a 32-scalar learned Gabor map on seeds
9100/9101. Gate 10b asks whether frequency/oscillation is needed for that
compact-map point.

All learned maps below have exactly 32 trainable geometry scalars, emit exactly
16 real values, and use the same 170-parameter linear 10-class head:

* POINT: 16 bilinear point samples x 2 coordinates = 32 scalars.
* GPAIR: 8 oriented Gaussian pairs x (x,y,separation,orientation) = 32 scalars;
  each pair emits its two lobe integrals. Two fixed lobe widths are reported;
  taking the stronger one is deliberately conservative against a Gabor-specific
  claim.

Data/splits/training are imported unchanged from gate10_mnist_scale_v2.py.
"""
from __future__ import annotations
import argparse, numpy as np, torch
from torch import nn
from torch.nn import functional as F
from gate10_mnist_scale_v2 import data, fit, SEEDS, C, M

torch.set_num_threads(2)

class PointSensors(nn.Module):
    def __init__(self, raw):
        super().__init__(); self.raw=nn.Parameter(raw.clone())
    def forward(self,x):
        # grid_sample uses (x,y) in [-1,1]. Keep a small image margin.
        q=.05+.90*torch.sigmoid(self.raw)
        grid=(2*q-1)[None,:,None,:].expand(len(x),-1,-1,-1)
        return F.grid_sample(x,grid,mode='bilinear',padding_mode='zeros',align_corners=True)[:,0,:,0]

class PointLinear(nn.Module):
    def __init__(self,raw): super().__init__(); self.s=PointSensors(raw); self.h=nn.Linear(M,C)
    def forward(self,x): return self.h(self.s(x))

class GaussianPairSensors(nn.Module):
    def __init__(self,raw,sigma):
        super().__init__(); self.raw=nn.Parameter(raw.clone()); self.sigma=float(sigma)
        yy,xx=torch.meshgrid(torch.linspace(0,1,28),torch.linspace(0,1,28),indexing='ij')
        self.register_buffer('xx',xx.clone()); self.register_buffer('yy',yy.clone())
    def forward(self,x):
        s=torch.sigmoid(self.raw); cx=.05+.90*s[:,0]; cy=.05+.90*s[:,1]
        sep=.03+.35*s[:,2]; th=np.pi*s[:,3]
        ux=torch.cos(th); uy=torch.sin(th)
        px1=cx-.5*sep*ux; py1=cy-.5*sep*uy; px2=cx+.5*sep*ux; py2=cy+.5*sep*uy
        def lobes(px,py):
            dx=self.xx[None]-px[:,None,None]; dy=self.yy[None]-py[:,None,None]
            g=torch.exp(-.5*(dx*dx+dy*dy)/(self.sigma*self.sigma))
            return g/(g.flatten(1).norm(dim=1)[:,None,None]+1e-8)
        g1=lobes(px1,py1); g2=lobes(px2,py2); im=x[:,0]
        return torch.cat([torch.einsum('bhw,nhw->bn',im,g1),torch.einsum('bhw,nhw->bn',im,g2)],1)

class GaussianPairLinear(nn.Module):
    def __init__(self,raw,sigma): super().__init__(); self.s=GaussianPairSensors(raw,sigma); self.h=nn.Linear(M,C)
    def forward(self,x): return self.h(self.s(x))

def one(root,download,seed):
    d=data(root,download,seed)
    pg=torch.Generator().manual_seed(300000+seed); praw=torch.randn(16,2,generator=pg)*.7
    gg=torch.Generator().manual_seed(100000+seed); graw=torch.randn(8,4,generator=gg)*.7
    out={}
    torch.manual_seed(400000+seed); out['point']=fit(PointLinear(praw),d.x,d.y,d.xv,d.yv,d.xt,d.yt,seed+101)
    for sigma,key in ((.12,'gpair12'),(.22,'gpair22')):
        torch.manual_seed(500000+seed+int(sigma*100)); out[key]=fit(GaussianPairLinear(graw,sigma),d.x,d.y,d.xv,d.yv,d.xt,d.yt,seed+200+int(sigma*100))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.mnist-data'); ap.add_argument('--download',action='store_true'); a=ap.parse_args()
    rows=[]
    for s in SEEDS:
        r=one(a.root,a.download,s); rows.append(r); print(f"seed {s}: point={r['point']:.4f} gpair12={r['gpair12']:.4f} gpair22={r['gpair22']:.4f}")
    print('\nGate 10b means (Gate10 learned-Gabor reference = 0.8833):')
    for k in ('point','gpair12','gpair22'): print(f'{k:<10}{np.mean([r[k] for r in rows]):.4f}')
    best=max(('gpair12','gpair22'),key=lambda k:np.mean([r[k] for r in rows]))
    print(f'best Gaussian-pair attacker = {best}')
if __name__=='__main__': main()
