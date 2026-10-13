from lib import *
spec={
 'L':dict(bg=(0.955,0.006,230),surface=(1,0,0),s2=(0.935,0.010,230),fg=(0.22,0.025,235),muted=(0.48,0.025,235),line=(0.88,0.012,235),linestrong=(0.62,0.02,235),
   accent=None,accsoft=(0.93,0.03,225),
   ok=(0.48,0.095,152),okon=(1,0,0),oktext=(0.46,0.095,152),oksoft=(0.95,0.03,152),
   warn=(0.82,0.150,78),warnon=(0.30,0.06,60),warntext=(0.50,0.115,55),warnsoft=(0.95,0.045,80),
   ng=(0.56,0.02,240),ngtext=(0.48,0.02,240),ngsoft=(0.93,0.008,240),
   flag=(0.48,0.15,25),band=(0.60,0.04,235),track=(0.935,0.010,230),mark=(0.22,0.025,235)),
 'D':dict(bg=(0.175,0.012,235),surface=(0.215,0.015,235),s2=(0.255,0.018,235),fg=(0.88,0.012,235),muted=(0.70,0.02,235),line=(0.31,0.018,235),linestrong=(0.54,0.02,235),
   accent=(0.72,0.095,225),accsoft=(0.30,0.04,225),
   ok=(0.62,0.105,152),okon=(0.20,0.03,152),oktext=(0.74,0.11,152),oksoft=(0.27,0.035,152),
   warn=(0.83,0.135,80),warnon=(0.24,0.04,70),warntext=(0.82,0.13,78),warnsoft=(0.29,0.04,75),
   ng=(0.60,0.02,240),ngtext=(0.70,0.02,235),ngsoft=(0.26,0.012,240),
   flag=(0.74,0.12,22),band=(0.55,0.04,235),track=(0.175,0.012,235),mark=(0.88,0.012,235)),
}
P={}
for mode,d in spec.items():
    p={}
    for k,v in d.items():
        if v is None: p[k]='#0d6c8c'; continue
        h,ok=from_oklch(*v); p[k]=h
        if not ok: print('gamut clip',mode,k,v)
    P[mode]=p
P['L']['accentfg']='#ffffff'; P['D']['accentfg']=from_oklch(0.22,0.04,225)[0]
import json; json.dump(P,open('pal.json','w'),indent=1)
for m,p in P.items():
    print(m,' '.join(f'{k}={v}' for k,v in p.items()))
