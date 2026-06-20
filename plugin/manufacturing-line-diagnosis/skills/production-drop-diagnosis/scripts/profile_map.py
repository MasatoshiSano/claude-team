#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""適応型データプロファイラ。任意のExcel/CSVを解析し、列を「標準概念」へ自動マッピングし、
"今できる分析" と "あると良いデータ→できる分析" と "確認したい項目" を出力する。
使い方: python profile_map.py <file.xlsx|file.csv>
固定スキーマに縛られず、別名・表記ゆれを吸収する。低信頼/未マップはユーザーに確認する候補として提示。"""
import sys, re, json
try:
    import pandas as pd
except ImportError:
    sys.exit("pandas が必要: pip install pandas openpyxl --break-system-packages")

# 標準概念 -> 別名(部分一致, 大小無視)
CONCEPTS = {
 "date":      ["日付","年月日","date","日にち","営業日"],
 "time":      ["時刻","日時","timestamp","datetime","生産時刻","開始日時","生産時間"],
 "plan_qty":  ["計画数","計画台数","計画個数","計画","目標","plan","target"],
 "actual_qty":["実績数","実績","生産数","生産台数","出来高","産出","actual","output","台数"],
 "model":     ["機種","品種","型式","品番","model","item","品目"],
 "serial":    ["シリアル","serial","製造番号","個体","sn","通し番号"],
 "good":      ["良品","良品数","合格","ok","good"],
 "defect":    ["不良","不良数","不適合","ng","defect","reject"],
 "defect_type":["不良項目","不良内容","不良モード","欠陥","defectmode"],
 "occur_proc":["発生工程","発生"],
 "outflow":   ["流出","検出","流出区分"],
 "stop_min":  ["停止","停止時間","停止(分)","ダウン","downtime","故障時間","停止分"],
 "stop_reason":["停止理由","事象","理由","内容","reason","現象"],
 "stop_cat":  ["区分","分類","category","ロス区分","停止区分"],
 "equipment": ["設備","号機","machine","設備id","eq","装置","機械"],
 "line":      ["ライン","line"],
 "process":   ["工程","process"],
 "site":      ["拠点","工場","site","plant"],
 "std_cycle": ["標準サイクル","標準時間","サイクルタイム","cycle","ct","標準pph","基準時間","タクト"],
 "input_qty": ["投入","投入数","受入","着工","input"],
 "sensor":    ["振動","温度","電流","圧力","vibration","センサ"],
 "cmms":      ["wo","作業指示","保全","故障コード","maintenance","作業内容"],
 "change4m":  ["4m","変化点","変更","変更内容","change"],
 "operator":  ["作業者","担当","operator","オペレータ","要員","氏名"],
 "doc":       ["手順","標準書","検査基準","sop","基準書","文書"],
}
LABEL={"date":"日付","time":"時刻","plan_qty":"計画数","actual_qty":"実績数","model":"機種","serial":"シリアル",
 "good":"良品数","defect":"不良数","defect_type":"不良項目","occur_proc":"発生工程","outflow":"流出区分",
 "stop_min":"停止時間","stop_reason":"停止理由","stop_cat":"停止区分","equipment":"設備","line":"ライン",
 "process":"工程","site":"拠点","std_cycle":"標準サイクル/PPH","input_qty":"投入数","sensor":"センサ値",
 "cmms":"保全履歴","change4m":"4M変化","operator":"作業者","doc":"手順/基準書"}

# 分析 -> 必要概念
CAPS=[
 ("製造三角図(日次)・達成率・悪化起点",["date","plan_qty","actual_qty"]),
 ("製造三角図(日内)",["time","actual_qty"]),
 ("計画/実績PPH(機種別)",["time","model","actual_qty"]),
 ("機種ズレ(遅れ型/順序)",["time","model","plan_qty"]),
 ("流動数曲線・仕掛",["date","input_qty","good"]),
 ("稼働率A・ダウンタイム時系列",["time","stop_min"]),
 ("ダウンタイムPareto(区分/設備)",["stop_min","equipment"]),
 ("性能P・OEE",["std_cycle","actual_qty","stop_min"]),
 ("品質Q・不良Pareto",["good","defect"]),
 ("発生/流出分析",["defect","occur_proc","outflow"]),
 ("bad-actor(慢性設備)",["cmms","equipment"]),
 ("予兆・状態基準保全(P-F)",["sensor","time"]),
 ("RCA起点(4M変化点)",["change4m"]),
 ("人要因(シフト相関)",["operator"]),
]

def norm(s): return re.sub(r"[\s\(\)（）_\-:：]","",str(s)).lower()

def map_columns(frames):
    found={}  # concept -> (sheet,col,conf)
    for sheet,df in frames.items():
        for col in df.columns:
            n=norm(col); runs=re.findall(r"[a-z]+", str(col).lower())
            for c,syns in CONCEPTS.items():
                conf=None
                for s in syns:
                    sn=norm(s)
                    if sn.isascii() and sn.isalpha() and len(sn)<=3:
                        # 短い英字略語(ct,ok,ng,eq…)は部分一致禁止。英字ラン完全一致のみ。
                        if sn in runs: conf="高" if n==sn else (conf or "中")
                        continue
                    if n==sn: conf="高"; break
                    if sn in n or n in sn: conf=conf or "中"
                if conf:
                    prev=found.get(c)
                    if not prev or (conf=="高" and prev[2]!="高"):
                        found[c]=(sheet,str(col),conf)
    return found

import os
def load_one(path):
    base=os.path.basename(path); low=path.lower(); fr={}
    if low.endswith((".xlsx",".xlsm")):
        xl=pd.ExcelFile(path)
        for s in xl.sheet_names:
            try: fr[f"{base}:{s}"]=pd.read_excel(xl,sheet_name=s,nrows=200)
            except Exception: pass
    elif low.endswith(".csv"):
        fr[base]=pd.read_csv(path,nrows=500)
    else:  # .txt .tsv その他テキスト: 区切り自動判定
        try: fr[base]=pd.read_csv(path,sep=None,engine="python",nrows=500)
        except Exception as e: print(f"  [読込失敗] {base}: {e}")
    return fr

def main(paths):
    frames={}
    for p in paths: frames.update(load_one(p))
    print("="*66);print(f"ファイル構造プロファイル: {', '.join(os.path.basename(p) for p in paths)}");print("="*66)
    for s,df in frames.items():
        print(f"\n[{s}]  行(サンプル){len(df)} 列{len(df.columns)}")
        print("  列:", ", ".join(map(str,df.columns))[:160])
    found=map_columns(frames); have=set(found)
    print("\n"+"-"*66);print("自動マッピング(標準概念 ← ファイル/シート:列 / 信頼度)");print("-"*66)
    for c in CONCEPTS:
        if c in found:
            sh,col,conf=found[c]; print(f"  {LABEL[c]:<14} ← [{sh}] {col}  ({conf})")
    print("\n"+"-"*66);print("✅ 今できる分析(データが揃っている)");print("-"*66)
    blocked=[]
    for name,req in CAPS:
        lack=[r for r in req if r not in have]
        if not lack: print(f"  ・{name}")
        else: blocked.append((name,lack))
    if not any(not [r for r in req if r not in have] for _,req in CAPS): print("  (まだ無し)")
    print("\n"+"-"*66);print("➕ あると良いデータ → できるようになる分析");print("-"*66)
    for name,lack in blocked:
        print(f"  ・{name}  ← 不足: {', '.join(LABEL.get(x,x) for x in lack)}")
    low=[c for c in found if found[c][2]=="中"]
    miss=[c for c in CONCEPTS if c not in found]
    print("\n"+"-"*66);print("❓ 確認したい項目(低信頼/未検出 → ユーザーに質問)");print("-"*66)
    for c in low:
        sh,col,_=found[c]; print(f"  ・「{col}」は {LABEL[c]} とみなしてよいですか?([{sh}])")
    if miss: print("  ・未検出(あれば列名を教えてください):", ", ".join(LABEL[m] for m in miss))
    if not low and not miss: print("  (高信頼でマップ済み)")

if __name__=="__main__":
    if len(sys.argv)<2: sys.exit("usage: python profile_map.py <file1> [file2 ...]")
    main(sys.argv[1:])
