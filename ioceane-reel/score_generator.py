import numpy as np, soundfile as sf, json, sys
from scipy.signal import butter, sosfilt, fftconvolve
tl=json.load(open(sys.argv[1])); out=sys.argv[2]
sr=44100; fps=tl['fps']; T=tl['total']/fps+2.5; n=int(T*sr); t=np.arange(n)/sr
rng=np.random.default_rng(7)
F=lambda f: int(f/fps*sr)
def lp(x,fc,o=2): return sosfilt(butter(o,fc,'low',fs=sr,output='sos'),x)
def hp(x,fc,o=2): return sosfilt(butter(o,fc,'high',fs=sr,output='sos'),x)
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],'band',fs=sr,output='sos'),x)
hz=lambda m: 440*2**((m-69)/12)
saw=lambda f,tt: 2*((f*tt)%1)-1
L=np.zeros(n); R=np.zeros(n)
def add(x,st,g=1.0,pan=0.0):
    e=min(n,st+len(x)); x=x[:e-st]
    L[st:e]+=x*g*(1-max(0,pan)); R[st:e]+=x*g*(1+min(0,pan))
end_music=F(tl['risers'][-1][0])  # silence gap before final hit
# --- drone: D1 + A1 + D2 low saws, slow swell, ducks before final hit
dr=np.zeros(n)
for m,g in ((26,0.5),(33,0.3),(38,0.25),(45,0.12)):
    for d in (-0.06,0.06): dr+=saw(hz(m)*2**(d/12),t)*g
mod=0.5+0.5*np.sin(2*np.pi*t/9)
cut=lp(dr,160)*(1-mod)+lp(dr,320)*mod
env=np.clip(t/3,0,1)*np.clip(1-(np.arange(n)-end_music)/(sr*0.6),0,1)
fin=F(tl['braams'][-1]); env[fin:]=np.clip(1-(np.arange(n-fin))/(sr*4),0,1)*0.8
add(cut*env,0,0.35)
# --- high shimmer pad
sh=sum(np.sin(2*np.pi*hz(m)*t+np.sin(t*0.7+m)) for m in (74,77,81,86))*0.03
add(sh*env,0,1.0)
# --- pulse ostinato (16ths, D minor), builds
p0,p1=F(tl['pulse'][0]),F(tl['pulse'][1]); step=60/120/4
notes=[50,50,62,50,57,50,60,50]
k=0; s=p0
while s<p1:
    L_=int(0.11*sr); tt=np.arange(L_)/sr; m=notes[k%8]
    x=lp(saw(hz(m),tt)+0.5*saw(hz(m)*1.005,tt),900+2500*(s-p0)/(p1-p0))*np.exp(-tt*28)
    prog=0.35+0.65*(s-p0)/(p1-p0)
    add(x,s,0.16*prog,pan=0.3 if k%2 else -0.3); k+=1; s+=int(step*sr)
# --- kick/taiko under pulse on beats
s=p0; b=0
while s<p1:
    tt=np.arange(int(0.5*sr))/sr
    kk=np.sin(2*np.pi*(40+120*np.exp(-tt*35))*tt)*np.exp(-tt*6)
    add(kk,s,0.55 if b%4==0 else 0.3); b+=1; s+=int(0.5*sr)
# --- hits: sub drop + noise crack + tom
for h in tl['hits']:
    st=F(h['f']); g=h['s']; tt=np.arange(int(2.5*sr))/sr
    sub=np.sin(2*np.pi*(30+70*np.exp(-tt*12))*tt)*np.exp(-tt*2.2)
    cr=lp(rng.standard_normal(len(tt)),3000)*np.exp(-tt*14)
    add(sub,st,0.9*g); add(cr,st,0.35*g)
    # whoosh into the hit
    wl=int(0.45*sr); wt=np.arange(wl)/sr
    w=bp(rng.standard_normal(wl),300,4000)*(wt/wt[-1])**2.5
    add(w,st-wl,0.18*g,pan=-0.4); add(w[::-1]*0.0,st,0)
# --- braams: big low brass-ish saw stacks
for bf in tl['braams']:
    st=F(bf); tt=np.arange(int(4*sr))/sr
    x=sum(saw(hz(m)*2**(d/12),tt) for m in (26,38,45,50) for d in (-0.1,0,0.1))
    # time-varying lowpass approx: blend two filters
    a=lp(x,1800); bb=lp(x,250); mix=np.exp(-tt*2.5)
    y=(a*mix+bb*(1-mix))*np.minimum(1,tt/0.02)*np.exp(-tt*0.9)
    add(np.tanh(y*0.4),st,0.5)
# --- risers: noise sweep + pitch rise
for a,b_ in tl['risers']:
    st,en=F(a),F(b_); l=en-st; tt=np.arange(l)/sr; pr=tt/tt[-1]
    nz=rng.standard_normal(l); out_=np.zeros(l)
    for i in range(8):
        seg=slice(i*l//8,(i+1)*l//8); out_[seg]=bp(nz,200+i*500,800+i*1200)[seg]
    tone=np.sin(2*np.pi*np.cumsum(200+1400*pr**2)/sr)*0.3
    add((out_+tone)*pr**2,st,0.3)
# reverb
ir_t=np.arange(int(2.2*sr))/sr; ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*3); ir=lp(ir,5000); ir/=np.abs(ir).sum()**0.5*8
L=L+fftconvolve(L,ir)[:n]*0.35; R=R+fftconvolve(R,ir[::-1].copy())[:n]*0.35
m=np.stack([hp(L,28),hp(R,28)],1); m=np.tanh(m/np.abs(m).max()*1.4); m/=np.abs(m).max(); m*=0.92
sf.write(out,m,sr)
print('ok',T)
