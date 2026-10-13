from lib import *
# public light: proposed
L=dict(surface='#ffffff',ok='#2d6d42',oks='#dff2e6',warn='#944e12',warnfill='#f9b73f',warnon='#43260a',warns='#fbeed6',ng='#6f7c88',ngs='#e7ebef',bg='#eef2f5',muted='#5a6977',s2='#f6f8fa')
D=dict(surface='#141f27',ok='#5aa572',oks='#13301f',warn='#f2b95a',warnfill='#f5bd56',warnon='#2b1c08',warns='#352612',ng='#7d8b98',ngs='#1d2830',bg='#0c1318',muted='#93a3b2',s2='#1a2832')
for n,c in (('L',L),('D',D)):
    print(n)
    for a,b in [('ok','surface'),('ok','oks'),('warn','surface'),('warn','warns'),('surface','ok'),('warnon','warnfill'),('warnfill','surface'),('ng','ngs'),('muted','surface'),('muted','bg'),('muted','s2')]:
        print(f'  {a}/{b} {c[a]} {c[b]} {cr(c[a],c[b]):.2f}')
    print('  lum ok:warnfill %.2f'%cr(c['ok'],c['warnfill']))
    for t in 'PDT': print('  ',t,'dOK ok-warnfill %.1f'%dok(sim(c['ok'],t),sim(c['warnfill'],t)))
