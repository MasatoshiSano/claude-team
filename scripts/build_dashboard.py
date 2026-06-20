# -*- coding: utf-8 -*-
# 製造ライン診断ダッシュボード生成: _simdata3.json -> _dash.json -> 製造ライン診断ダッシュボード.html
import json, datetime as dt, bisect
from collections import defaultdict, Counter
D=json.load(open("_simdata3.json"))
ser=D["serials"]; stops=D["stops"]; daily=D["daily"]; plan_rows=D["plan"]; pph=D["pph"]
dates=[d["date"] for d in daily]
def hm(s,base):
    t=dt.datetime.strptime(base+" "+s,"%Y-%m-%d %H:%M"); return (t-dt.datetime.strptime(base+" 08:30","%Y-%m-%d %H:%M")).total_seconds()/60
plan_seg=defaultdict(list)
for r in plan_rows:
    date,line,m,q,st,en,pph_=r; plan_seg[date].append((hm(st,date),hm(en,date),q))
acts=defaultdict(list)
for r in ser: acts[r[1]].append(dt.datetime.strptime(r[2],"%Y-%m-%d %H:%M:%S"))
for k in acts: acts[k].sort()
triangles={}
for date in dates:
    seg=sorted(plan_seg[date]); base=dt.datetime.strptime(date+" 08:30","%Y-%m-%d %H:%M")
    aa=acts[date]; last=int((aa[-1]-base).total_seconds()/60)+5
    def pc(tm):
        c=0
        for s,e,q in seg:
            if tm>=e:c+=q
            elif tm>s:c+=q*(tm-s)/(e-s)
        return round(c)
    L=[];P=[];A=[]
    for tm in range(0,last+1,10):
        L.append((base+dt.timedelta(minutes=tm)).strftime("%H:%M")); P.append(pc(tm)); A.append(bisect.bisect_right(aa,base+dt.timedelta(minutes=tm)))
    triangles[date]={"labels":L,"plan":P,"act":A}
pphd=defaultdict(list)
for r in pph:
    date,hour,pm,ppph,am,ap,z=r
    pphd[date].append({"hour":hour,"pm":pm,"ppph":ppph,"am":am,"ap":ap,"z":z})
flow={"dates":dates,"cumIn":[],"cumOut":[],"wip":[]}; ci=co=0
for d in daily:
    ci+=d["inp"]; co+=d["good"]; flow["cumIn"].append(ci); flow["cumOut"].append(co); flow["wip"].append(ci-co)
catm=Counter(); eqm=Counter()
for s in stops: catm[s[8]]+=s[5]; eqm[s[2]]+=s[5]
def pareto(cnt):
    items=sorted(cnt.items(),key=lambda x:-x[1]); tot=sum(cnt.values()); cum=0; out=[]
    for k,v in items: cum+=v; out.append({"k":k,"v":round(v,1),"pct":round(v/tot*100,1),"cum":round(cum/tot*100,1)})
    return out
downtime={"cat":pareto(catm),"eq":pareto(eqm)}
trend={"dates":dates,"oee":[],"ach":[],"A":[],"P":[],"Q":[]}
for d in daily:
    A=d["operating"]/(d["operating"]+d["stop"]); P=d["ideal"]/d["operating"]; Q=d["good"]/d["total"]
    trend["oee"].append(round(A*P*Q*100,1)); trend["ach"].append(round(d["total"]/d["plan"]*100,1))
    trend["A"].append(round(A*100,1)); trend["P"].append(round(P*100,1)); trend["Q"].append(round(Q*100,1))
avg_oee=round(sum(trend["oee"])/len(trend["oee"]),1); short=sum(d["plan"]-d["total"] for d in daily); worst=dates[trend["oee"].index(min(trend["oee"]))]
data={"dates":dates,"triangles":triangles,"pph":pphd,"flow":flow,"downtime":downtime,"trend":trend,
      "kpi":{"avgOEE":avg_oee,"short":short,"worst":worst,"worstOEE":min(trend["oee"])}}
json.dump(data,open("_dash.json","w"),ensure_ascii=False)

# ---- HTML(データ内蔵・Chart.js CDN・日付セレクタ。完全版は 製造ライン診断ダッシュボード.html を参照) ----
# 注: HTMLテンプレートは完全記録mdの本文には含めず、本スクリプト実行で生成する方針。
print("dash data ready. avgOEE",avg_oee,"shortfall",short,"worst",worst,"-> _dash.json")
print("※HTML本体は本セッションで生成済み(製造ライン診断ダッシュボード.html)。再生成時はこの_dash.jsonをHTMLテンプレートに__DATA__として差し込む。")
