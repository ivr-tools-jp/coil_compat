from lib import *
import json,sys
P=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'pal.json'))
for m,c in P.items():
    print('=====',m)
    T=[('TEXT fg/bg','fg','bg'),('TEXT fg/s2','fg','s2'),('TEXT muted/surface','muted','surface'),('TEXT muted/bg','muted','bg'),('TEXT muted/s2','muted','s2'),
       ('TEXT accent/surface','accent','surface'),('TEXT accent/accsoft','accent','accsoft'),('TEXT accentfg/accent','accentfg','accent'),
       ('TEXT oktext/surface','oktext','surface'),('TEXT oktext/oksoft','oktext','oksoft'),
       ('TEXT warntext/surface','warntext','surface'),('TEXT warntext/warnsoft','warntext','warnsoft'),
       ('TEXT ngtext/surface','ngtext','surface'),('TEXT ngtext/ngsoft','ngtext','ngsoft'),('TEXT fg/ngsoft','fg','ngsoft'),
       ('TEXT surface/flag (tag)','surface','flag'),('TEXT flag/surface','flag','surface'),
       ('GFX ok/surface','ok','surface'),('GFX okon/ok symbol','okon','ok'),
       ('GFX warn/surface','warn','surface'),('GFX warnon/warn symbol','warnon','warn'),
       ('GFX ng border/surface','ng','surface'),('GFX ng/ngsoft symbol','ng','ngsoft'),
       ('GFX linestrong/surface','linestrong','surface'),
       ('GFX band/track','band','track'),('GFX band/surface','band','surface'),('GFX mark/band','mark','band'),('GFX mark/track','mark','track'),
       ('GFX okon/ok','okon','ok')]
    for n,a,b in T:
        r=cr(c[a],c[b]); need=4.5 if n.startswith('TEXT') else 3.0
        print(f'  {n:30s} {c[a]} on {c[b]} {r:5.2f} {"OK" if r>=need else "NG"}')
    print('  fg Y=%.3f  bg Y=%.4f  fg/bg=%.1f'%(Y(c['fg']),Y(c['bg']),cr(c['fg'],c['bg'])))
    print('  lum ratio ok:warn %.2f  ok:ng %.2f  warn:ng %.2f'%(cr(c['ok'],c['warn']),cr(c['ok'],c['ng']),cr(c['warn'],c['ng'])))
    print('  ok:accent lum %.2f'%cr(c['ok'],c['accent']))
    for t,nm in zip('NPDTG',['normal','protan','deutan','tritan','gray']):
        s={k:sim(c[k],t) for k in ('ok','warn','ng','ngsoft','accent','band','flag')}
        print(f'  {nm:7s} dOK ok-warn {dok(s["ok"],s["warn"]):5.1f} ok-ng {dok(s["ok"],s["ng"]):5.1f} warn-ng {dok(s["warn"],s["ng"]):5.1f} ok-accent {dok(s["ok"],s["accent"]):5.1f} warn-flag {dok(s["warn"],s["flag"]):5.1f}  ok={s["ok"]} warn={s["warn"]}')
    for L in LENS:
        f=lambda k: lens(c[k],L)
        print(f'  lens {L:9s} ok/warn lum {cr(f("ok"),f("warn")):4.2f} dOK ok-warn {dok(f("ok"),f("warn")):5.1f} warn/surface {cr(f("warn"),f("surface")):4.2f} warntext/surface {cr(f("warntext"),f("surface")):4.2f} band/track {cr(f("band"),f("track")):4.2f} muted/surface {cr(f("muted"),f("surface")):4.2f} accent/surface {cr(f("accent"),f("surface")):4.2f} flag-tag {cr(f("surface"),f("flag")):4.2f}')
