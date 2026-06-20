# -*- coding: utf-8 -*-
import random, datetime as dt, json
from collections import defaultdict, Counter
random.seed(42)
MODELS={"A":7.5,"B":10.0,"C":12.0,"D":9.0,"E":11.0}
def std_pph(m): return round(3600/MODELS[m])
LINE="L-01"; BN="M-12"; START=dt.date(2026,6,1)
def wd(i):
    d=START;c=0
    while True:
        if d.weekday()<5:
            c+=1
            if c==i:return d
        d+=dt.timedelta(days=1)
DAYS=10
DP={
 1:dict(models=["A","B","C"],spd=0.98,down=12,coovr=0,defect=0.008,vib=2.1,suf=0.20),
 2:dict(models=["A","B","D"],spd=0.99,down=10,coovr=2,defect=0.008,vib=2.0,suf=0.20),
 3:dict(models=["B","C","D","E"],spd=0.96,down=18,coovr=3,defect=0.010,vib=2.3,suf=0.25),
 4:dict(models=["A","C","E"],spd=0.98,down=14,coovr=1,defect=0.009,vib=2.2,suf=0.20),
 5:dict(models=["A","B","C","D"],spd=0.95,down=22,coovr=4,defect=0.012,vib=3.0,suf=0.30),
 6:dict(models=["A","B","C"],spd=0.90,down=30,coovr=10,defect=0.018,vib=4.1,suf=0.50),
 7:dict(models=["A","B","C","D","E"],spd=0.82,down=65,coovr=16,defect=0.032,vib=5.6,breakdown=38,suf=0.50),
 8:dict(models=["A","C","D"],spd=0.80,down=58,coovr=14,defect=0.035,vib=6.2,suf=0.50),
 9:dict(models=["B","C","E"],spd=0.85,down=40,coovr=8,defect=0.026,vib=4.4,suf=0.40),
 10:dict(models=["A","B","D","E"],spd=0.88,down=32,coovr=6,defect=0.020,vib=3.8,suf=0.35),
}
PCO=20; TGT=440; SS=dt.time(8,30); CAP=600   # 生産開始 8:30 (朝礼 8:00-8:30は計画停止), 最大18:30
dpress=["圧入深さNG","圧入荷重ばらつき"]; dother=["外観キズ","端子曲がり","ラベル不良"]
serials=[];stops=[];defects=[];daily=[];plan_rows=[];pph_rows=[];g=0
def seg_build(models):
    seg=[];t=0.0;per=TGT/len(models)
    for i,m in enumerate(models):
        if i>0:t+=PCO
        q=int(round(per*60/MODELS[m]));st=t;t+=q*MODELS[m]/60.0
        seg.append(dict(model=m,qty=q,start=st,end=t))
    return seg
def pmat(seg,tm):
    for s in seg:
        if s["start"]<=tm<s["end"]:return s["model"]
    return seg[0]["model"] if tm<seg[0]["start"] else "計画完了後"
def fmt(d): return d.strftime("%Y-%m-%d %H:%M:%S")

for i in range(1,DAYS+1):
    p=DP[i];date=wd(i);seg=seg_build(p["models"]);date_s=str(date)
    pq=sum(s["qty"] for s in seg)
    for s in seg:
        plan_rows.append([date_s,LINE,s["model"],s["qty"],
            (dt.datetime.combine(date,SS)+dt.timedelta(minutes=s["start"])).strftime("%H:%M"),
            (dt.datetime.combine(date,SS)+dt.timedelta(minutes=s["end"])).strftime("%H:%M"),std_pph(s["model"])])
    bd_plan=p.get("breakdown",0)
    bd=round(random.triangular(bd_plan*0.6,bd_plan*1.8,bd_plan),1) if bd_plan else 0   # 復帰ばらつき
    suf=p["suf"]; su_budget=round((p["down"]-bd_plan)*suf); sc_budget=p["down"]-bd_plan-su_budget
    nco=max(1,len(seg)-1); su_per=su_budget/nco
    ev=[]
    if bd: ev.append((random.uniform(120,300),bd,BN,"設備故障(圧入機)","BR","設備故障"))
    rem=sc_budget
    while rem>3:
        d=round(min(rem,random.uniform(1.5,5.5)),1);tt=random.uniform(20,CAP-30)
        if random.random()<0.7: eq=BN;reason="チョコ停(ワーク詰まり)";code="MS";cat="チョコ停"
        else: eq=random.choice(["M-08","M-15","M-20"]);reason="軽微停止";code="MN";cat="軽微停止"
        ev.append((tt,d,eq,reason,code,cat));rem-=d
    ev.sort()
    clock=0.0;ei=0;op=0.0;idl=0.0;d_stop=0.0;d_co=0.0;d_su=0.0;d_fp=0.0;tot=0;good=0;ndef=0
    sd=dt.datetime.combine(date,SS)
    def addstop(eq,reason,code,cat,mins):
        global clock,d_stop,d_co,d_su,d_fp
        st=sd+dt.timedelta(minutes=clock)
        stops.append([date_s,LINE,eq,reason,code,round(mins,1),fmt(st),fmt(st+dt.timedelta(minutes=mins)),cat])
        clock+=mins
        if code in("MS","MN","BR"):d_stop+=mins
        elif code=="CO":d_co+=mins
        elif code=="SU":d_su+=mins
        elif code=="FP":d_fp+=mins
    def flush(clk):
        global ei
        while ei<len(ev) and ev[ei][0]<=clk:
            tt,d,eq,reason,code,cat=ev[ei]; addstop(eq,reason,code,cat,d); ei+=1
    for ci,s in enumerate(seg):
        if clock>=CAP:break
        if ci==0:
            addstop("M-20","初物検査(ライン外・朝一番)","FP","初物検査",random.uniform(15,28))  # 朝礼後の初物
        else:
            addstop(BN,"段取り替え","CO","段取り",PCO+p["coovr"]/nco)
            addstop("M-20","初物検査(ライン外)","FP","初物検査",random.uniform(4,9))
            if su_per>0:
                k=1 if su_per<3 else 2
                for _ in range(k): addstop(BN,"立上げ調整(段取り直後)","SU","段取り立上げ",su_per/k)
        m=s["model"];ideal=MODELS[m];ac=ideal/p["spd"];made=0
        while made<s["qty"] and clock<CAP:
            flush(clock)
            if clock>=CAP:break
            ts=sd+dt.timedelta(minutes=clock);clock+=ac/60.0;op+=ac/60.0;idl+=ideal/60.0
            g+=1;made+=1;tot+=1;pm=pmat(seg,clock)
            ng=random.random()<(p["defect"]*(1.6 if made<=3 else 1.0))
            lot="LOT-2206B" if i>=6 else "LOT-2205A"
            if ng:
                if random.random()<0.72: dty=random.choice(dpress);occ="圧入";oeq=BN;det=random.random()<0.6
                else: dty=random.choice(dother);occ=random.choice(["加工","組立","検査"]);oeq="M-08";det=random.random()<0.9
                of="出荷(流出)" if not det else "工程内検出";ndef+=1
                defects.append([f"SN{g:07d}",ts.strftime("%Y-%m-%d %H:%M"),m,occ,oeq,dty,"発生",of,lot]);judge="NG"
            else: good+=1;judge="OK"
            serials.append([f"SN{g:07d}",date_s,fmt(ts),LINE,BN,m,pm,
                            ("ズレ" if pm!=m and pm!="計画完了後" else ""),judge,round(ac,2),lot,
                            ("段取り直後" if (made<=2 and ci>0) else "")])
    flush(CAP)
    daily.append(dict(date=date_s,plan=pq,total=tot,good=good,defect=ndef,operating=round(op,1),
        stop=round(d_stop,1),co=round(d_co,1),su=round(d_su,1),fp=round(d_fp,1),ideal=round(idl,1),vib=p["vib"],inp=pq,
        start=serials_first_time if False else None))
    bucket=defaultdict(lambda:defaultdict(int))
    for r in serials:
        if r[1]==date_s: bucket[r[2][11:13]][r[5]]+=1
    for h in range(8,19):
        tt0=(h-8.5)*60+30.0;pm=pmat(seg,tt0);within=seg[0]["start"]<=tt0<seg[-1]["end"]
        ppph=std_pph(pm) if (within and pm in MODELS) else 0
        am="/".join(sorted(bucket[f"{h:02d}"].keys()));ap=sum(bucket[f"{h:02d}"].values())
        if within or ap>0:
            pph_rows.append([date_s,f"{h:02d}:00",pm if within else "—",ppph,am,ap,
                ("ズレ" if (pm in MODELS) and am and (pm not in am.split("/")) else "")])

# ---- asserts ----
cd=Counter();cg=Counter();cn=Counter()
for r in serials: cd[r[1]]+=1;cg[r[1]]+=(r[8]=="OK");cn[r[1]]+=(r[8]=="NG")
for d in daily:
    assert cd[d["date"]]==d["total"] and cg[d["date"]]==d["good"] and cn[d["date"]]==d["defect"]
    assert d["good"]+d["defect"]==d["total"]
assert len(defects)==sum(d["defect"] for d in daily)
ums=Counter()
for s in stops:
    if s[4] in("MS","BR","MN"):ums[s[0]]+=s[5]
for d in daily: assert abs(ums[d["date"]]-d["stop"])<0.6
for d in daily: assert 1500<=d["total"]<=5200,(d["date"],d["total"])
# linkage: no serial inside any stop window (seconds precision)
serT=defaultdict(list)
for r in serials: serT[r[1]].append(dt.datetime.strptime(r[2],"%Y-%m-%d %H:%M:%S"))
viol=0
for s in stops:
    st=dt.datetime.strptime(s[6],"%Y-%m-%d %H:%M:%S");en=dt.datetime.strptime(s[7],"%Y-%m-%d %H:%M:%S")
    viol+=sum(1 for t in serT[s[0]] if st< t <en)
assert viol==0, f"serials inside stop windows: {viol}"
print("ALL ASSERTS PASSED (停止窓内シリアル0 = 生産停止と完全連動)")
# morning start times & metrics
print("朝一番の初回生産時刻:")
firstt={}
for r in serials:
    if r[1] not in firstt: firstt[r[1]]=r[2][11:19]
for d in daily: print(" ",d["date"],"初回",firstt[d["date"]],"plan",d["plan"],"act",d["total"],
    "stop",d["stop"],"co",d["co"],"su",d["su"],"初物",d["fp"])
json.dump(dict(serials=serials,stops=stops,defects=defects,daily=daily,plan=plan_rows,pph=pph_rows),
          open("_simdata3.json","w"))
print("serials",len(serials),"stops",len(stops),"-> _simdata3.json")
