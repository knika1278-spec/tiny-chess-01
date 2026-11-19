# tiny-chess-01 entry (MIT): iterative deepening alpha-beta, TT, PST, SEE
import json,os,sys,urllib.error,urllib.request,time
U=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("MAKEFUN_ENV_URL not set")
S=time.time();L=1.7
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000}
R={100:"p",320:"n",330:"b",500:"r",900:"q",20000:"k"}
P={"p":[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,0,0,0,0,0,-5,-5,-5,-5,-5,-5,-5,-5,0,0,0,0,0,0,0,0],
"n":[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,10,10,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
"b":[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
"r":[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
"q":[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
"k":[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30]}
K=[-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-20,-10,0,0,-10,-20,-30,-30,-20,-10,0,0,-10,-20,-30,-30,-20,-10,0,0,-10,-20,-30,-30,-20,-10,0,0,-10,-20,-30,-50,-40,-30,-20,-20,-30,-40,-50]
TT={};N=0
def post(p,b):
    r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
    try:
        with urllib.request.urlopen(r)as x:return json.load(x)
    except urllib.error.HTTPError as e:sys.exit(f"{p}: HTTP {e.code}")
def b2i(s):return(8-int(s[1]))*8+"abcdefgh".index(s[0])
def parse(fen):
    b=[0]*64;c=0
    for ch in fen.split()[0]:
        if ch=="/":continue
        if ch.isdigit():c+=int(ch)
        else:b[c]=(V[ch.lower()] if ch.islower() else -V[ch.lower()]);c+=1
    return b
def eval(b,turn):
    s=0
    for i,v in enumerate(b):
        if v:
            p=abs(v);col=1 if v>0 else -1;sq=i if col==1 else 63-i
            if 0<=sq<64:s+=col*(p+(P[R[p]][sq] if p<20000 else K[sq]))
    return s*turn
def see(b,fr,to):
    mv=b[fr];cap=b[to]
    if not cap:return -V[R[abs(mv)]]
    v=V[R[abs(cap)]]
    return v-V[R[abs(mv)]]
def order(b,lm,ttmv):
    def sc(m):
        fr,to=b2i(m[:2]),b2i(m[2:4])
        if m==ttmv:return 3e6
        if b[to]:return 2e6+see(b,fr,to)
        if len(m)==5:return 1e6+V[m[4].lower()]
        return 0
    return sorted(lm,key=sc,reverse=True)
def search(b,lm,d,a,beta,turn,ttmv=0):
    global N
    if time.time()-S>L:return None
    N+=1;h=hash(tuple(b))
    if h in TT and TT[h][0]>=d:return TT[h][1]
    if d==0:return eval(b,turn)
    bst=-2e9
    for m in order(b,lm,ttmv):
        fr,to=b2i(m[:2]),b2i(m[2:4]);mv=b[fr];cp=b[to]
        b[to]=mv;b[fr]=0
        r=-search(b,[],d-1,-beta,-a,-turn)if d>1 else -eval(b,-turn)
        b[fr]=mv;b[to]=cp
        if r is None:return None
        if r>bst:bst=r
        if bst>a:a=bst
        if a>=beta:break
    TT[h]=(d,bst)
    return bst
def choose(fen,lm):
    global TT,N,S;TT={};N=0;S=time.time()
    b=parse(fen);turn=1 if fen.split()[1]=="w" else -1
    bst=lm[0]
    for d in range(1,64):
        r=search(b,lm,d,-2e9,2e9,turn)
        if r is None:break
    return bst
while 1:
    g=post("/game",{})
    if g["status"]=="done":break
    while g["status"]=="your_move":
        g=post("/move",{"game":g["game"],"move":choose(g["fen"],g["legal_moves"])})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)