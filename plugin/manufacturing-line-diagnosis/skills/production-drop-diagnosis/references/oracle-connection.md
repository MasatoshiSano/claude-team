# オンプレOracle ライブ接続(リアルタイム取得)

クラウド側からは社内Oracleに直接届かない。**Oracleに到達できる端末(社内PC)で抽出を実行**し、出力を診断に渡す。
Desktop Commander 経由でClaudeが実行してもよいし、端末で直接実行してもよい。資格情報は環境変数に置き、チャット/クラウドに渡さない。

## セットアップ(端末側・1回だけ)
1. ドライバ導入(Oracleクライアント不要のthinモード):
   ```
   pip install oracledb pandas openpyxl
   ```
2. 環境変数に接続情報を設定(PWはここだけ):
   - macOS/Linux:
     ```
     export ORA_USER=PROD_RO
     export ORA_PASSWORD='********'
     export ORA_DSN=10.0.0.12:1521/ORCLPDB1     # host:port/service_name
     ```
   - Windows(PowerShell):
     ```
     $env:ORA_USER="PROD_RO"; $env:ORA_PASSWORD="********"; $env:ORA_DSN="10.0.0.12:1521/ORCLPDB1"
     ```
3. 接続テスト: `python oracle_pull.py --check`  → 「接続OK」

## ライブ抽出 → 診断
```
python oracle_pull.py --sql references/extract_template.sql --out today.csv
python profile_map.py today.csv          # 列を標準概念へマップ(任意)
python diagnose.py today.xlsx            # テンプレ形式なら直接診断
```
- `extract_template.sql` は列を標準概念名(日付/実績数/設備…)にエイリアス済み → 出力がそのまま診断フォーマット。
- **リアルタイム性**: SQLの `WHERE 日付 >= TRUNC(SYSDATE)-N` や `>= SYSDATE - 1` で現在時刻基準に絞れば、実行ごとに最新値。必要なら数分間隔で再実行/スケジュール化。

## Desktop Commander で自動実行(Claudeから起動)
Desktop Commander はユーザPC上で動くため、上記コマンドをClaudeが端末に投げてライブ取得→診断まで一気に回せる。
資格情報は端末の環境変数にあるので、Claude(クラウド)はPWを見ない。

## セキュリティ/ガバナンス
- 専用の**読み取り専用・最小権限**アカウント(例: PROD_RO)を使う。
- 抽出は**オンプレ実行**。PWはファイルに書かず環境変数 or Oracleウォレット。
- 必要な列だけSELECT。個人情報があればSQL側でマスク。
- 出力CSVの保管場所に注意(共有/クラウド同期フォルダを避ける)。

## スキーマが不明なとき
列・テーブル名が分からなければ、まず構造を調べる:
```
python oracle_pull.py --query "SELECT table_name FROM user_tables ORDER BY table_name" --out tables.csv
python oracle_pull.py --query "SELECT column_name,data_type FROM user_tab_columns WHERE table_name='PROD_DAILY'" --out cols.csv
```
取得した列一覧を profile_map の考え方で標準概念に当て、extract_template.sql のエイリアスを実列名へ置換する。
