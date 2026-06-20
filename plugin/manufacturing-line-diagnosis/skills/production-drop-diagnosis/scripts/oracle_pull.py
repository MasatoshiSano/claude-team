#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""オンプレOracleからライブで生産データを抽出し、診断フォーマットのCSVに出力する。
資格情報は環境変数から読む(チャット/クラウドに渡さない):
  ORA_USER, ORA_PASSWORD, ORA_DSN   (DSN例: 10.0.0.12:1521/ORCLPDB1)
このスクリプトは Oracle に到達できる端末(社内PC等)で実行する。Desktop Commander 経由でも端末直接でも可。
依存: python-oracledb (thinモード。Oracleクライアント不要)  ->  pip install oracledb

使い方:
  python oracle_pull.py --check                      # 接続テストのみ
  python oracle_pull.py --sql query.sql --out out.csv# SQLファイルを実行しCSV出力
  python oracle_pull.py --query "SELECT ..." --out out.csv
ポイント: SQL側で列を標準概念名にエイリアス(例: AS "日付", AS "実績数")すると、
出力CSVがそのまま診断フォーマットになり、profile_map/diagnose に直接渡せる。
リアルタイム性: WHERE 日付 >= TRUNC(SYSDATE)-N のように現在時刻基準で絞れば、実行ごとに最新値が取れる。"""
import os, sys, csv, argparse

def get_conn():
    try:
        import oracledb
    except ImportError:
        sys.exit("python-oracledb が必要です: pip install oracledb")
    u=os.environ.get("ORA_USER"); p=os.environ.get("ORA_PASSWORD"); dsn=os.environ.get("ORA_DSN")
    miss=[k for k,v in [("ORA_USER",u),("ORA_PASSWORD",p),("ORA_DSN",dsn)] if not v]
    if miss:
        sys.exit("環境変数が未設定: "+", ".join(miss)+"  (例: export ORA_DSN=10.0.0.12:1521/ORCLPDB1)")
    return oracledb.connect(user=u, password=p, dsn=dsn)   # thinモード(クライアント不要)

def run(sql, out):
    conn=get_conn()
    try:
        cur=conn.cursor(); cur.execute(sql)
        cols=[d[0] for d in cur.description]
        w=open(out,"w",encoding="utf-8-sig",newline="") if out else sys.stdout
        cw=csv.writer(w); cw.writerow(cols); n=0
        for row in cur:
            cw.writerow(["" if v is None else v for v in row]); n+=1
        if out: w.close(); print(f"出力: {out}  ({n}行, 列: {', '.join(cols)})")
        else: print(f"\n# {n}行", file=sys.stderr)
    finally:
        conn.close()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="接続テストのみ")
    ap.add_argument("--sql", help="SQLファイル")
    ap.add_argument("--query", help="SQL文字列")
    ap.add_argument("--out", help="出力CSV(省略時は標準出力)")
    a=ap.parse_args()
    if a.check:
        c=get_conn()
        cur=c.cursor(); cur.execute("SELECT 1 FROM dual"); cur.fetchone()
        print("接続OK:", os.environ.get("ORA_DSN")); c.close(); return
    sql = open(a.sql,encoding="utf-8").read() if a.sql else a.query
    if not sql: sys.exit("--sql か --query を指定してください")
    run(sql, a.out)

if __name__=="__main__":
    main()
