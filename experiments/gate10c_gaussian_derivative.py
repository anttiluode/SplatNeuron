"""Gate 10c: matched nonoscillatory steerable Gaussian-derivative attacker.

Eight branches, four geometry scalars each (x,y,scale,orientation), two real
responses per branch (first and second directional Gaussian derivatives):
32 learned map scalars, 16 outputs, same 170-param linear head as Gate 10.

This is a stronger test of whether Gabor's oscillatory/frequency form is needed
than point or positive Gaussian-pair sampling.
"""
from __future__ import annotations
import argparse, numpy as np, torch
from torch import nn
from gate10_mnist_scale_v2 import data, fit, SEEDS, M, C

torch.set_num_threads(2)

class GaussianDerivativeSensors(nn.Module):
    def __init__(self,raw):
        super().__init__(); self.raw=nn.Parameter(raw.clone())
        yy,xx=torch.meshgrid(torch.linspace(0,1,28),torch.linspace(0,1,28),indexing='ij')
        self.register_buffer('xx',xx.clone()); self.register_buffer('yy',yy.clone())
    def forward(self,x):
        s=torch.sigmoid(self.raw)
        cx=.05+.90*s[:,0]; cy=.05+.90*s[:,1]
        sigma=.05+.25*s[:,2]; th=np.pi*s[:,3]
        dx=self.xx[None]-cx[:,None,None]; dy=self.yy[None]-cy[:,None,None]
        co=torch.cos(th)[:,None,None]; si=torch.sin(th)[:,None,None]
        xr=co*dx+si*dy; yr=-si*dx+co*dy; sg=sigma[:,None,None]
        env=torch.exp(-.5*(xr*xr+yr*yr)/(sg*sg))
        odd=(xr/sg)*env
        even=((xr*xr)/(sg*sg)-1.0)*env
        odd=odd/(odd.flatten(1).norm(dim=1)[:,None,None]+1e-8)
        even=even/(even.flatten(1).norm(dim=1)[:,None,None]+1e-8)
        im=x[:,0]
        return torch.cat([torch.einsum('bhw,nhw->bn',im,odd),torch.einsum('bhw,nhw->bn',im,even)],1)

class Model(nn.Module):
    def __init__(self,raw): super().__init__(); self.s=GaussianDerivativeSensors(raw); self.h=nn.Linear(M,C)
    def forward(self,x): return self.h(self.s(x))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.mnist-data'); ap.add_argument('--download',action='store_true'); a=ap.parse_args()
    scores=[]
    for seed in SEEDS:
        d=data(a.root,a.download,seed)
        raw=torch.randn(8,4,generator=torch.Generator().manual_seed(100000+seed))*.7
        torch.manual_seed(600000+seed)
        acc=fit(Model(raw),d.x,d.y,d.xv,d.yv,d.xt,d.yt,seed+300)
        scores.append(acc); print(f'seed {seed}: gaussian_derivative={acc:.4f}')
    print(f'\nmean gaussian_derivative={np.mean(scores):.4f}')
    print('Gate10 learned-Gabor reference=0.8833; same 32 map scalars / 16 outputs.')
if __name__=='__main__': main()
