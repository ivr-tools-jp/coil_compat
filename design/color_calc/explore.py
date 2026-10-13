from lib import *
for n,h in [('accent',"#0d6c8c"),('okL',"#15804a"),('warnL',"#ad6208"),('ngL','#6d7a85'),('okD','#4cc27f'),('warnD','#eba43d'),('accD','#5bbad8'),('fgD','#e2eaef'),('bgD','#091015')]:
    L,C,H=oklch(h); print(n,h,f'L={L:.3f} C={C:.3f} H={H:.0f} Y={Y(h):.3f}', 'sims:',[sim(h,t) for t in 'PDT'])
# current proto: ok vs accent under CVD
for t in 'NPDT':
    print(t,'okL-accent dOK %.1f'%dok(sim('#15804a',t),sim('#0d6c8c',t)), 'okL-warnL %.1f'%dok(sim('#15804a',t),sim('#ad6208',t)),'okD-warnD %.1f'%dok(sim('#4cc27f',t),sim('#eba43d',t)),'okD-accD %.1f'%dok(sim('#4cc27f',t),sim('#5bbad8',t)))
print('cr okD warnD',cr('#4cc27f','#eba43d'),'okD accD',cr('#4cc27f','#5bbad8'))
