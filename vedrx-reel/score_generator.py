import numpy as np, soundfile as sf, json, sys
from scipy.signal import butter, sosfilt, fftconvolve
tl=json.load(open(sys.argv[1])); out=sys.argv[2]
sr=44100; fps=tl['fps']; T=tl['total']/fps+1.0; n=int(T*sr); t=np.arange(n)/sr
rng=np.random.default_rng(3); F=lambda f:int(f/fps*sr)
lp=lambda x,fc:sosfilt(butter(2,fc,'low',fs=sr,output='sos'),x)
hp=lambda x,fc:sosfilt(butter(2,fc,'high',fs=sr,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=sr,output='sos'),x)
hz=lambda m:440*2**((m-69)/12); saw=lambda f,tt:2*((f*tt)%1)-1
L=np.zeros(n); R=np.zeros(n)
def add(x,st,g=1.0,pan=0.0):
    if st<0: x=x[-st:]; st=0
    e=min(n,st+len(x)); x=x[:e-st]; L[st:e]+=x*g*(1-max(0,pan)); R[st:e]+=x*g*(1+min(0,pan))
ln={l['id']:l for l in tl['lines']}
drop0,drop1=F(ln['l08']['start']),F(ln['l09']['start'])
endf=F(ln['l13']['start'])
bpm=110; beat=60/bpm; bar=4*beat
prog=[[57,60,64,69],[53,57,60,65],[48,52,55,60],[55,59,62,67]]  # Am F C G  (hopeful)
bass=[33,29,36,31]
# section gain envelope
gain=np.ones(n); gain[:F(ln['l03']['start'])]=0.55
gain[drop0:drop1]=0.0
# pads (strings)
pad=np.zeros(n); sub=np.zeros(n); arp=np.zeros(n)
for b in range(int(T/bar)+1):
    c=prog[b%4]; st=int(b*bar*sr); en=min(n,st+int(bar*sr)+int(0.4*sr))
    if st>=n: break
    tt=np.arange(en-st)/sr; env=np.minimum(1,tt/0.5)*np.minimum(1,(len(tt)/sr-tt)/0.4)
    for m in c:
        for d in (-0.07,0,0.07): pad[st:en]+=saw(hz(m)*2**(d/12),tt)*env*0.03
    sub[st:en]+=np.sin(2*np.pi*hz(bass[b%4])*tt)*env*0.3
    for k in range(16):
        s2=st+int(k*beat/4*sr); 
        if s2>=n: break
        e2=min(n,s2+int(0.25*sr)); tk=np.arange(e2-s2)/sr; m=c[[0,1,2,3,2,1,2,3][k%8]]+12
        arp[s2:e2]+=(np.sin(2*np.pi*hz(m)*tk)+0.3*np.sin(4*np.pi*hz(m)*tk))*np.exp(-tk*14)*0.05
pad=lp(pad,1800)
arpg=np.clip((t-ln['l03']['start']/fps)/1.0,0,1)  # arps enter at l03
add(pad*gain,0,1); add(sub*gain,0,1); add(arp*gain*arpg,0,1,pan=0.2)
# drums: kick 4otf + clap from l05
s=F(ln['l03']['start']); k=0
while s<n:
    if not (drop0<=s<drop1) and s<F(tl['total'])-sr:
        tt=np.arange(int(0.35*sr))/sr
        add(np.sin(2*np.pi*(45+110*np.exp(-tt*30))*tt)*np.exp(-tt*9),s,0.5)
        if k%2==1 and s>F(ln['l05']['start']):
            add(bp(rng.standard_normal(int(0.2*sr)),900,5000)*np.exp(-np.arange(int(0.2*sr))/sr*25),s,0.12)
        hh=s+int(beat/2*sr); th=np.arange(int(0.05*sr))/sr
        add(hp(rng.standard_normal(len(th)),7000)*np.exp(-th*80),hh,0.05,pan=-0.3)
    s+=int(beat*sr); k+=1
# hits + whooshes on every line start (except l02, l04 lighter)
for l in tl['lines']:
    st=F(l['start']); g=1.0 if l['id'] in ('l01','l03','l05','l09','l13') else 0.55
    tt=np.arange(int(1.6*sr))/sr
    add(np.sin(2*np.pi*(32+80*np.exp(-tt*14))*tt)*np.exp(-tt*2.8),st,0.7*g)
    add(lp(rng.standard_normal(len(tt)),2500)*np.exp(-tt*16),st,0.25*g)
    wl=int(0.35*sr); wt=np.arange(wl)/sr; w=bp(rng.standard_normal(wl),400,5000)*(wt/wt[-1])**2.2
    add(w,st-wl,0.14*g,pan=-0.3)
# word-level ticks on list lines (shot changes)
for lid in ('l05','l06','l07','l10'):
    for w in ln[lid]['words']:
        st=F(w['f']); tt=np.arange(int(0.25*sr))/sr
        add(bp(rng.standard_normal(len(tt)),2000,8000)*np.exp(-tt*30),st,0.08)
# riser into the drop + reverse swell into l09
a,b=F(ln['l07']['start']+20),drop0; l_=b-a; tt=np.arange(l_)/sr; pr=tt/tt[-1]
add((bp(rng.standard_normal(l_),300,6000)*0.6+np.sin(2*np.pi*np.cumsum(220+1500*pr**2)/sr)*0.3)*pr**2.5,a,0.3)
# low drone during drop
tt=np.arange(drop1-drop0)/sr; add(lp(saw(hz(33),tt)+saw(hz(40),tt),300)*np.minimum(1,tt/0.3)*0.25,drop0,0.5)
sw=int(0.8*sr); tt=np.arange(sw)/sr; add(bp(rng.standard_normal(sw),200,6000)*(tt/tt[-1])**3,drop1-sw,0.3)
# end: fade
fade=np.clip((T-1.0-t)/2.0,0,1); L*=fade; R*=fade
ir_t=np.arange(int(1.8*sr))/sr; ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*3.5); ir=lp(ir,6000); ir/=np.abs(ir).sum()**0.5*8
L=L+fftconvolve(L,ir)[:n]*0.3; R=R+fftconvolve(R,ir[::-1].copy())[:n]*0.3
m=np.stack([hp(L,30),hp(R,30)],1); m=np.tanh(m/np.abs(m).max()*1.3); m/=np.abs(m).max(); m*=0.9
sf.write(out,m,sr); print('ok',T)
