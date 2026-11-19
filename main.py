# tiny-chess-01 entry (MIT): 10x12 mailbox, negamax alpha-beta, quiescence, null move,
# TT move ordering, iterative deepening on a fixed node budget (no clock, so replays match).
import json,os,sys,urllib.request as Q
U=os.environ["MAKEFUN_ENV_URL"];L=120000;M=30000
V=dict(P=100,N=320,B=330,R=500,Q=900,K=60000)
Z="KKKKUUUUMMOQLLMPKKKOLJIKLMMGKKKKACEECGKKEKMNELNOEKNOELMNCGKLACEEGIIIIKKKIKLMILLMIKMMIMMMILKKGIIIKKKKLMMMJKKKJKKKJKKKJKKKJKKKKKKLGIIJIKKKIKLLJKLLJKLLILLLIKLKGIIJECCAECCAECCAECCAGEECIGGGOOKKOQMKACEGEGIKEIOQEIQSEIQSEIOQEEKKAEEE"
def mk(k,o):return[0]*21+sum(([V[k]+5*(ord(Z[o+r*4+min(f,7-f)])-75)for f in range(8)]+[0,0]for r in range(8)),[])+[0]*19
T={k:mk(k,32*i)for i,k in enumerate("PNBRQK")};KM=T["K"];KE=mk("K",192)
n,e,s,w=-10,1,10,-1
D=dict(P=(n,2*n,n+w,n+e),N=(2*n+e,2*n+w,n+2*e,s+2*e,2*s+e,2*s+w,s+2*w,n+2*w),B=(n+e,s+e,s+w,n+w),R=(n,e,s,w))
D["Q"]=D["K"]=D["B"]+D["R"]
def gen(b):
 for i,p in enumerate(b):
  if p.isupper():
   for d in D[p]:
    j=i+d
    while 1:
     q=b[j]
     if q.isspace()or q.isupper():break
     if p=="P":
      if d in(n,2*n)and q!=".":break
      if d==2*n and(i<81 or b[i+n]!="."):break
      if d in(n+w,n+e)and q==".":break
     yield i,j
     if p in"PNK"or q.islower():break
     j+=d
def rot(b):return b[::-1].swapcase()
def mv(b,m):
 i,j=m;p=b[i];b=list(b);b[j]="Q"if p=="P"and j<29 else p;b[i]="."
 return rot("".join(b))
def val(b,m):
 i,j=m;p=b[i];q=b[j];x=T[p][j]-T[p][i]
 if q.islower():x+=T[q.upper()][119-j]
 if p=="P"and j<29:x+=T["Q"][j]-T["P"][j]
 return x
def E(b):return sum(T[p][i]if p.isupper()else-T[p.upper()][119-i]for i,p in enumerate(b)if p.isalpha())
class X(Exception):pass
def S(b,sc,d,a,be,nl=1):
 global N
 N+=1
 if N>L:raise X
 if sc<-M:return-2*M-d
 q=d<1
 if q:
  if sc>=be:return sc
  a=max(a,sc);bs=sc
 else:
  bs=-3*M
  if nl and d>2 and sc>=be:
   r=-S(rot(b),-sc,d-3,-be,1-be,0)
   if r>=be:return r
 t=H.get(b)
 for m in sorted((m for m in gen(b)if not q or b[m[1]].islower()or b[m[0]]=="P"and m[1]<29),key=lambda m:(m!=t,-val(b,m))):
  r=-S(mv(b,m),-sc-val(b,m),d-1,-be,-a)
  if r>bs:
   bs=r
   if r>a:
    a=r;H[b]=m
    if a>=be:break
 if bs<-M and not q:
  o=rot(b)
  if not any(o[j]=="k"for i,j in gen(o)):return 0
 return bs
def think(ks,P):
 global N,H
 N=0;H={};bm=ks[0][0]
 if len(ks)<2:return bm
 for d in range(1,99):
  a=-4*M
  try:
   for u,c in sorted(ks,key=lambda k:k[0]!=bm):
    r=0 if c in P else-S(c,E(c),d-1,-4*M,-a)
    if r>a:a=r;bm=u
  except X:break
  if a>M:break
 return bm
def sq(u,wt):k=21+"abcdefgh".index(u[0])+10*(8-int(u[1]));return k if wt else 119-k
def ap(b,u,wt):
 i,j=sq(u[:2],wt),sq(u[2:4],wt);p=b[i];b=list(b)
 if p=="K"and abs(j-i)==2:
  d=(j-i)//2;k=j
  while b[k]!="R":k+=d
  b[k]=".";b[j-d]="R"
 if p=="P"and b[j]=="."and(j-i)%10:b[j+10]="."
 b[j]=u[4:].upper()or p;b[i]="."
 return rot("".join(b))
I=" "*20+" rnbqkbnr  pppppppp "+" ........ "*4+" PPPPPPPP  RNBQKBNR "+" "*20
def post(p,d):
 with Q.urlopen(Q.Request(U+p,json.dumps(d).encode(),{"content-type":"application/json"}))as r:return json.load(r)
if __name__=="__main__":
 g=post("/game",{})
 while g["status"]!="done":
  if g["status"]=="your_move":
   b=I;wt=1;P={b}
   for u in g["moves"]:b=ap(b,u,wt);wt^=1;P.add(b)
   lm=g["legal_moves"]
   try:
    T["K"]=KE if sum(V[p.upper()]for p in b if p in"NBRQnbrq")<2600 else KM
    u=think([(u,ap(b,u,wt))for u in lm],P)
   except Exception:u=lm[0]
   g=post("/move",{"game":g["game"],"move":u})
  else:
   print(g["game"],g["opponent_name"],g["colour"],g["outcome"],g["reason"],g["plies"],file=sys.stderr);g=post("/game",{})
 print("done",g["wins"],g["draws"],g["losses"],file=sys.stderr)
