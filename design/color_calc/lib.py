import math
def h2r(h):
    h=h.lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def unlin(c): c=max(0,min(1,c)); return 12.92*c if c<=0.0031308 else 1.055*c**(1/2.4)-0.055
def tohex(rgb): return '#'+''.join('%02x'%round(max(0,min(1,x))*255) for x in rgb)
def Y(h): r,g,b=[lin(x) for x in h2r(h)]; return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b):
    la,lb=Y(a),Y(b); return (max(la,lb)+.05)/(min(la,lb)+.05)
def mix(fg,bg,p):
    f,b=h2r(fg),h2r(bg); return tohex([p*x+(1-p)*y for x,y in zip(f,b)])
M={'P':[[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
   'D':[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
   'T':[[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
def sim(h,t):
    if t=='N': return h
    if t=='G':  # achromatic (luminance only)
        y=Y(h); return tohex([unlin(y)]*3)
    l=[lin(x) for x in h2r(h)]; m=M[t]
    return tohex([unlin(sum(m[i][j]*l[j] for j in range(3))) for i in range(3)])
def oklab(h):
    r,g,b=[lin(x) for x in h2r(h)]
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b
    m=0.2119034982*r+0.6806995451*g+0.1073969566*b
    s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l,m,s=[math.copysign(abs(x)**(1/3),x) for x in (l,m,s)]
    return (0.2104542553*l+0.7936177850*m-0.0040720468*s,
            1.9779984951*l-2.4285922050*m+0.4505937099*s,
            0.0259040371*l+0.7827717662*m-0.8086757660*s)
def oklch(h):
    L,a,b=oklab(h); return L,math.hypot(a,b),(math.degrees(math.atan2(b,a))%360)
def from_oklch(L,C,H):
    a=C*math.cos(math.radians(H)); b=C*math.sin(math.radians(H))
    l=L+0.3963377774*a+0.2158037573*b; m=L-0.1055613458*a-0.0638541728*b; s=L-0.0894841775*a-1.2914855480*b
    l,m,s=l**3,m**3,s**3
    r=4.0767416621*l-3.3077115913*m+0.2309699292*s
    g=-1.2684380046*l+2.6097574011*m-0.3413193965*s
    bb=-0.0041960863*l-0.7034186147*m+1.7076147010*s
    return tohex([unlin(x) for x in (r,g,bb)]), all(-0.001<=x<=1.001 for x in (r,g,bb))
def dok(a,b): return 100*math.dist(oklab(a),oklab(b))
# lens filters (speculative): multiply linear RGB
LENS={'amber':(0.95,0.78,0.35),'gray50':(0.5,0.5,0.5),'yellowish':(1.0,0.95,0.7)}
def lens(h,k):
    f=LENS[k]; return tohex([unlin(lin(x)*m) for x,m in zip(h2r(h),f)])
