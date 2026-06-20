#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ライン診断Excelを読み、固定フロー(いつ→どこ→何が)の起点指標を算出する。
使い方: python diagnose.py <xlsx>
依存: pandas, openpyxl
出力: 計画vs実績/OEE(A/P/Q)/ダウンタイムPareto/機種ズレ/悪化起点 を標準出力に。
欠落シートはスキップし「データ欠落」を所見として表示する。"""
import sys, json
try:
    import pandas as pd
except ImportError:
    sys.exit("pandas が必要です: pip install pandas openpyxl --break-system-packages")

def load(xl, name):
    try: return pd.read_excel(xl, sheet_name=name)
    except Exception: return None

def main(path):
    xl = pd.ExcelFile(path)
    sheets = xl.sheet_names
    out = {"file": path, "sheets": sheets, "missing": [], "findings": {}}
    need = ["日次サマリ","停止ログ","生産実績_シリアル"]
    for n in need:
        if n not in sheets: out["missing"].append(n)

    # ---- 何が: 日次 計画/実績/OEE ----
    ds = load(xl,"日次サマリ")
    daily=[]
    if ds is not None:
        for _,r in ds.iterrows():
            op=r.get("実働(分)"); st=r.get("停止(分)"); idl=r.get("標準時間(分)")
            good=r.get("良品数"); tot=r.get("実績数"); plan=r.get("計画数")
            try:
                A=op/(op+st); P=idl/op; Q=good/tot; oee=A*P*Q; ach=tot/plan
            except Exception:
                A=P=Q=oee=ach=None
            daily.append(dict(date=str(r.get("日付")),plan=plan,act=tot,ach=ach,A=A,P=P,Q=Q,oee=oee))
        out["findings"]["daily"]=daily
        # 悪化起点 = 達成率<98% または OEE が前日比 -0.05 を最初に割る日
        origin=None
        for i,d in enumerate(daily):
            if d["ach"] is not None and d["ach"]<0.98: origin=d["date"]; break
            if i>0 and d["oee"] and daily[i-1]["oee"] and d["oee"]<daily[i-1]["oee"]-0.05:
                origin=d["date"]; break
        out["findings"]["origin_day"]=origin

    # ---- どこ: 機種ズレ(遅れ型/順序) ----
    ser = load(xl,"生産実績_シリアル")
    if ser is not None and "機種ズレ" in ser.columns:
        z = ser.groupby("日付")["機種ズレ"].apply(lambda c:(c=="ズレ").sum())
        out["findings"]["zure_by_day"]={str(k):int(v) for k,v in z.items()}

    # ---- どこ: 計画/実績PPH(時間×機種) ----
    pp = load(xl,"時間別PPH")
    if pp is not None:
        cols=list(pp.columns)
        def find(key): return next((c for c in cols if key in str(c)), None)
        cP,aP,zC,dC = find("計画PPH"),find("実績PPH"),find("機種ズレ"),find("日付")
        if cP and aP and dC:
            rows=[]
            for d,g in pp.groupby(dC):
                plan=g[cP].fillna(0); act=g[aP].fillna(0)
                inplan=plan>0
                short=int(((act<plan*0.8)&inplan).sum())          # 実績が計画の8割未満の時間帯
                zure=int((g[zC]=="ズレ").sum()) if zC else 0       # 機種ズレ時間帯
                gap=(plan-act).where(inplan,0)
                worst=g.loc[gap.idxmax(),find("時間")] if find("時間") and len(gap) and gap.max()>0 else None
                rows.append(dict(date=str(d),hours=int(inplan.sum()),short_hours=short,
                                 zure_hours=zure,worst_hour=str(worst) if worst is not None else None,
                                 worst_gap=round(float(gap.max()),0) if len(gap) else 0))
            out["findings"]["pph_by_day"]=rows

    # ---- 何が: ダウンタイム Pareto ----
    st = load(xl,"停止ログ")
    if st is not None:
        col="区分" if "区分" in st.columns else None
        mincol="停止(分)" if "停止(分)" in st.columns else None
        if col and mincol:
            cat=st.groupby(col)[mincol].sum().sort_values(ascending=False)
            tot=cat.sum(); cum=0; rows=[]
            for k,v in cat.items():
                cum+=v; rows.append(dict(k=k,min=round(v,1),pct=round(v/tot*100,1),cum=round(cum/tot*100,1)))
            out["findings"]["downtime_cat"]=rows
        if "設備" in st.columns and mincol:
            eq=st.groupby("設備")[mincol].sum().sort_values(ascending=False)
            out["findings"]["downtime_eq"]=[dict(eq=str(k),min=round(v,1)) for k,v in eq.items()]

    # ---- print ----
    print("="*64)
    print(f"ライン診断: {path}")
    print(f"シート数 {len(sheets)} / 欠落: {out['missing'] or 'なし'}")
    print("="*64)
    if daily:
        print("\n[WHAT] 日次 計画 vs 実績 / OEE")
        print(f"{'日付':<12}{'計画':>6}{'実績':>6}{'達成率':>8}{'A':>7}{'P':>7}{'Q':>7}{'OEE':>7}")
        for d in daily:
            f=lambda x: f"{x*100:5.1f}%" if isinstance(x,(int,float)) else "   -  "
            print(f"{d['date']:<12}{int(d['plan']):>6}{int(d['act']):>6}{f(d['ach']):>9}{f(d['A']):>8}{f(d['P']):>8}{f(d['Q']):>8}{f(d['oee']):>8}")
        print(f"\n  → 悪化起点(推定): {out['findings'].get('origin_day')}")
    if "zure_by_day" in out["findings"]:
        print("\n[WHERE] 機種ズレ件数(日別) ※順序保持の右シフト=遅れ型")
        for k,v in out["findings"]["zure_by_day"].items(): print(f"  {k}: {v}")
    if "pph_by_day" in out["findings"]:
        print("\n[WHERE] 計画/実績PPH(時間別) ※実績PPH<計画PPHの時間帯=性能ロス, 機種ズレ時間=遅れ")
        print(f"  {'日付':<12}{'有効h':>6}{'PPH不足h':>9}{'機種ズレh':>9}{'最悪時間':>10}{'最大差':>7}")
        for r in out["findings"]["pph_by_day"]:
            print(f"  {r['date']:<12}{r['hours']:>6}{r['short_hours']:>9}{r['zure_hours']:>9}{str(r['worst_hour']):>10}{int(r['worst_gap']):>7}")
    if "downtime_cat" in out["findings"]:
        print("\n[WHAT] ダウンタイム Pareto(区分別)")
        for r in out["findings"]["downtime_cat"]:
            print(f"  {r['k']:<10} {r['min']:>7}分  {r['pct']:>5}%  累計{r['cum']:>5}%")
    if "downtime_eq" in out["findings"]:
        print("\n[WHAT] ダウンタイム(設備別)")
        for r in out["findings"]["downtime_eq"][:6]:
            print(f"  {r['eq']:<8} {r['min']:>7}分")
    print("\n[次の手] 起点日の停止ログ/設備トラブル/4M変化/センサを確認 → OEE主因で4Mの当たり → root-cause-analysis-copilot へ。")
    print("\n--- machine-readable ---")
    print(json.dumps(out, ensure_ascii=False, default=str))

if __name__=="__main__":
    if len(sys.argv)<2: sys.exit("usage: python diagnose.py <xlsx>")
    main(sys.argv[1])
