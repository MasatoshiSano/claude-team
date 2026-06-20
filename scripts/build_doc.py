# -*- coding: utf-8 -*-
import os
BASE="pbuild/mlp"
SK=BASE+"/skills"
PDD=SK+"/production-drop-diagnosis"
out=[]
def w(s): out.append(s)
def embed(title, path, lang="text"):
    try: c=open(path,encoding="utf-8").read()
    except Exception as e: c=f"(読み込み失敗: {e})"
    w(f"\n#### {title}\n\n`{path.replace('pbuild/mlp/','')}`\n")
    w("````"+lang)   # 4バックティック: 内部の```を壊さない
    w(c.rstrip("\n"))
    w("````\n")

w("""# 製造ライン診断 — セッション完全記録(ハンドブック)

> 本書はこのセッションで設計・作成した「製造ライン診断プラグイン」と関連成果物の**完全な記録**です。
> 方法論、プラグインの全ファイル全文(コピペ可)、シミュレーションデータ設計、適応型データ取り込み、
> オンプレOracleライブ連携、運用手順、取り込み/作成したスキルの棚卸し、再現スクリプトまでを収録しています。
> 対象: 製造業(ディスクリート/装置)の生産・保全・品質チーム。

---

## 目次
1. 背景と目的(経緯)
2. 取り込んだ/作成した プラグイン・スキル 一覧
3. 診断方法論(コア知識)
4. プラグイン全体構成と全ファイル全文
5. シミュレーションデータ設計(19シート・シナリオ・真因)
6. 診断ダッシュボード
7. 適応型データ取り込み(任意フォーマット対応)
8. オンプレOracle ライブ連携
9. 運用手順(日本語指示→診断)
10. 今後の拡張候補
11. 付録: 再現スクリプト
12. 付録: インストール時のトラブル
13. 付録: 信頼性スキル集(18スキル)の評価
14. 付録: production-scheduling 選定の経緯
15. 付録: テストデータ検証(別フォーマット適応)
16. 付録: ダッシュボード生成スクリプト
17. 付録: 隣接領域の連携(生産計画・人員配置・在庫管理)
18. 付録: 人員配置最適化(配置最適)

---

## 1. 背景と目的(経緯)

出発点は「コミュニティ製の信頼性スキル集(Rob-Reliability/reliability-skills-for-clane)は装置産業の設備保全向けで、
生産ラインのラインバランス最適化・ボトルネック分析とは別物」という整理だった。そこから、生産現場の
**「最近、生産数が落ちている・稼働率が悪い、なぜか」をデータから切り分ける**ことを目的に据えた。

検討の中で、次の道具立てが「一枚で多くを語る」ことを確認した:

- **製造三角図**(横軸=時刻/縦軸=累計個数、計画線と実績線)。実績線が横ばい=設備停止、傾き<計画=効率低下、傾きのばらつき=リズム不良、立上がり遅れ=朝礼・初物検査。
- **流動数曲線**(累計投入 vs 累計完成)。縦差=仕掛(WIP)、横差=リードタイム。2本が開く=滞留(ボトルネック)。
- **計画・実績PPH(時間×機種)**。機種をそろえてペース差を見る。計画機種≠実績機種は「遅れ型(順序保持で右シフト)」と「順序間違い型」に分かれ、遅れ型が多い。
- **OEE分解**(可用性×性能×品質)、**ダウンタイム分析**、**RCA(根本原因分析)**。
- **4M(人・機械・材料・方法)** と **発生原因/流出原因** の日本式フレーム。

結論として、原因特定の核ループ(現象特定→OEE→RCA→対策)を**1つのプラグイン**にまとめ、
不足していた「可視化+自動診断+OEE→RCAグルー+4M/発生流出+任意データ取り込み+DBライブ連携」を新規スキルとして作成した。

""")

w("""## 2. 取り込んだ/作成した プラグイン・スキル 一覧

### 2.1 既にインストール済みだったプラグイン(本セッション開始時)
- engineering / product-management / design / desktop-commander(knowledge-work-plugins)
- claude-engineering-skills(流体・ポンプ・CFD等)
- tier-a-skills(コードレビュー/リファクタリング/TDD/アーキレビュー/**NCR品質保証(8D/FMEA/特性要因図)**/組立手順書/構造解析/Jira)
  - → 8D・NCR・特性要因図・FEAは既存プラグインでカバー済みのため**新規作成せず**(重複回避)。

### 2.2 新規作成プラグイン: `manufacturing-line-diagnosis`(本セッションの主成果)
ライセンス: Apache-2.0 AND MIT。6スキル構成。バージョン推移 0.1.0→0.4.0。

| スキル | 区分 | 役割 | 出典/ライセンス |
|---|---|---|---|
| production-scheduling | 取り込み(核) | スケジューリング/ボトルネック(TOC・DBR)/ラインバランス/SMED/OEE | affaan-m/everything-claude-code, **Apache-2.0** |
| root-cause-analysis-copilot | 取り込み(核) | 構造化RCA(証拠ゲート・物理/人/潜在・人のミスで止めない) | Rob-Reliability, **MIT** |
| bad-actor-analysis | 取り込み(補完) | 慢性的に足を引く設備をPareto特定→RCA候補化 | Rob-Reliability, **MIT** |
| fmea-generation | 取り込み(補完) | FMEA/FMECAドラフト(IEC60812/SAE J1739/ISO14224) | Rob-Reliability, **MIT** |
| pm-optimization | 取り込み(補完) | 故障モードに紐づかない形骸PMの洗い出し | Rob-Reliability, **MIT** |
| **production-drop-diagnosis** | **新規作成** | 生産数低下の原因特定。固定フロー+読み筋+OEE→RCAグルー+4M/発生流出+適応取り込み+Oracleライブ | 本セッション, MIT |

`production-drop-diagnosis` の同梱物:
- scripts: `diagnose.py`(Excel→計画実績/OEE/Pareto/機種ズレ/悪化起点)、`profile_map.py`(任意ファイルの構造解析+概念マッピング+ケイパビリティ提示)、`oracle_pull.py`(オンプレOracleライブ抽出)
- references: `reading-rules.md`、`field-dictionary.md`、`extract_template.sql`、`oracle-connection.md`

### 2.3 補助成果物(プラグイン外)
- `manufacturing-line-sim-data.xlsx` — 整合性保証のシミュレーションデータ(19シート、生産実績26,000+シリアル行)
- `製造ライン診断ダッシュボード.html` — 6グラフ・日付セレクタ・データ内蔵で再オープン可
- `testdata/`(A_production.csv, A_downtime.csv, B_stop_log.txt, C_partial.xlsx)— 別フォーマット検証用
- 再現スクリプト: `gen_sim3.py`(データ生成)、`build_all3.py`(Excel構築)
""")

w("""## 3. 診断方法論(コア知識)

### 3.1 固定診断フロー(順番を崩さない)
**WHEN いつ → WHERE どこ → WHAT 何が → WHY なぜ → FIX 対策**
1. WHEN: 製造三角図で悪化の起点(傾き変化・横ばい)を特定。
2. WHERE: 流動数曲線(仕掛・滞留)+ 計画/実績PPH(時間×機種・機種ズレ)で時間帯と機種を絞る。
3. WHAT: OEE分解(可用性×性能×品質)+ ダウンタイムPareto(区分別・設備別)で主ロスを特定。
4. WHY: RCA(root-cause-analysis-copilot)。4Mで広げ、発生/流出を分け、証拠ゲートで掘る。
5. FIX: bad-actor/FMEA/PM最適化へ展開し標準化で閉じる。

### 3.2 読み筋(現象→意味)
- 実績線が横ばい → 設備停止(可用性ロス)
- 傾き<計画 → 性能ロス(速度低下・チョコ停)
- 傾きのばらつき → リズム不良(段取り・平準化)
- 立上がり遅れ → 朝礼・初物検査
- 機種ズレ(順序保持の右シフト) → 遅れ型。起点機種の遅れ内訳=段取り超過/稼働PPH不足/前工程の遅れ継承
- 機種ズレ(順序入替) → 順序間違い型(指示・方法)
- ダウンタイムが段取り直後に集中 → 段取り/立上げ(SMED)。突発故障は別に切り分け

### 3.3 OEE定義(本テンプレ準拠)
- 稼働率A = 実働 /(実働+停止)  ※停止=計画外(設備故障/チョコ停/軽微)
- 性能P = 標準時間 / 実働
- 品質Q = 良品 / 実績
- OEE = A×P×Q  (段取りCO・立上げSU・初物検査FPは別管理)

### 3.4 OEE主因 → RCA起点(4Mの当たり)
- 可用性ロス主因 → 機械・方法(故障・段取り・保全)
- 性能ロス主因 → 機械・材料(治具摩耗・速度・材料ロット)
- 品質ロス主因 → 材料・方法・人(不良項目・発生工程)

### 3.5 4M と 発生/流出
- 4M(人・機械・材料・方法)で横に広げてから縦に掘る(特性要因図の骨)。4M変化点を必ず確認。
- 不良は必ず**発生原因(なぜ作った)**と**流出原因(なぜ止められなかった)**の2系統。対策は発生防止+流出防止。
- 樹形図そのものは事前に固定しない。固定するのは作法(4Mで広げる・発生/流出を分ける・証拠で裏取り・人のミスで止めない)だけ。RCA本体は root-cause-analysis-copilot に接続。
""")

w("""## 4. プラグイン全体構成と全ファイル全文

```
manufacturing-line-diagnosis/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── production-drop-diagnosis/   (新規)
    │   ├── SKILL.md
    │   ├── scripts/{diagnose.py, profile_map.py, oracle_pull.py}
    │   └── references/{reading-rules.md, field-dictionary.md, extract_template.sql, oracle-connection.md}
    ├── production-scheduling/SKILL.md
    ├── root-cause-analysis-copilot/SKILL.md
    ├── bad-actor-analysis/SKILL.md
    ├── fmea-generation/SKILL.md
    └── pm-optimization/SKILL.md
```

### 4.1 マニフェスト / README""")
embed("plugin.json", BASE+"/.claude-plugin/plugin.json","json")
embed("README.md", BASE+"/README.md","markdown")

w("\n### 4.2 新規スキル production-drop-diagnosis")
embed("SKILL.md", PDD+"/SKILL.md","markdown")
embed("scripts/diagnose.py", PDD+"/scripts/diagnose.py","python")
embed("scripts/profile_map.py", PDD+"/scripts/profile_map.py","python")
embed("scripts/oracle_pull.py", PDD+"/scripts/oracle_pull.py","python")
embed("references/reading-rules.md", PDD+"/references/reading-rules.md","markdown")
embed("references/field-dictionary.md", PDD+"/references/field-dictionary.md","markdown")
embed("references/extract_template.sql", PDD+"/references/extract_template.sql","sql")
embed("references/oracle-connection.md", PDD+"/references/oracle-connection.md","markdown")

w("\n### 4.3 取り込みスキル(核・補完)")
embed("production-scheduling/SKILL.md", SK+"/production-scheduling/SKILL.md","markdown")
embed("root-cause-analysis-copilot/SKILL.md", SK+"/root-cause-analysis-copilot/SKILL.md","markdown")
embed("bad-actor-analysis/SKILL.md", SK+"/bad-actor-analysis/SKILL.md","markdown")
embed("fmea-generation/SKILL.md", SK+"/fmea-generation/SKILL.md","markdown")
embed("pm-optimization/SKILL.md", SK+"/pm-optimization/SKILL.md","markdown")

w("""## 5. シミュレーションデータ設計(19シート・シナリオ・真因)

整合性を保証するため、**離散イベントシミュレーション**で生成(停止・段取り・サイクルタイムから出来高・OEE・累計・仕掛を導出し、全シート相互整合をassertで検証)。

### 5.1 シナリオ(架空ライン L-01 / 大阪工場 JP-OSA / 10稼働日 2026-06-01〜12)
- 機種A〜E(標準サイクル 7.5〜12秒)、1日3〜5機種を順次生産、1シリアル=1行(計26,000+行/日2,000〜3,000)。
- 生産開始8:30(朝礼8:00-8:30)。各機種の量産前に初物検査(ライン外):朝一番15〜28分、切替時4〜9分 → 初回生産は概ね8:45〜8:56でばらつく。
- 機種切替直後に立上げダウン(SU)を注入 → 計画外ダウンの約半分が段取り直後に集中(現実準拠)。突発故障は切替と無関係に発生(復帰時間にばらつき)。
- 設備トラブル中はシリアルが1個も生産されない(停止窓内シリアル0で検証=生産停止と完全連動)。

### 5.2 植え込んだ真因(_答え_シナリオ シート)
- 物理: ボトルネック圧入機 M-12 の圧入治具クッション材摩耗 → 荷重ばらつき → チョコ停増・圧入深さNG。
- 引き金: 6/6 の材料ロット変更(LOT-2206B,硬度上振れ)で治具負荷増→摩耗加速。
- 人/方法: ロット変更時の条件再設定なし=変化点管理欠落。6/3新人配置は赤ニシン(悪化は6/6以降)。
- 潜在: 治具予防交換基準なし(PM形骸化)。最終検査に圧入深さ測定なし(流出)。
- 結果: 6/8以降にOEE低下(〜0.68)、達成率76.9%(6/9)、機種ズレ急増、仕掛拡大。

### 5.3 シート一覧(19)
説明 / 計画 / 生産実績_シリアル / 停止ログ / 不良データ / 設備トラブル情報 / ダウンタイム集計 /
時間別PPH / 日次サマリ(OEE計算式) / 設備マスタ(拠点-ライン-工程の3ツリー) / 機種マスタ /
ダウンタイム理由コード / 稼働カレンダー / 標準・手順書一覧 / 4M変化記録 / 作業者割当 /
センサ_振動 / 保全履歴_CMMS / _答え_シナリオ

### 5.4 整合性(検証済みの恒等式)
- 良品+不良=実績、不良明細件数=NG数、停止ログ合計=日次停止、仕掛=累計投入−累計完成、OEE=A×P×Q(計算式エラー0)。
""")

w("""## 6. 診断ダッシュボード

`製造ライン診断ダッシュボード.html`。データ内蔵の自己完結HTML(Chart.js CDN)。再オープン可能。
- KPI(平均OEE/取りこぼし/最悪日)
- ① 製造三角図(日付セレクタで全10日)② 計画・実績PPH(機種ズレは赤)③ 流動数曲線 ④ OEE・達成率推移 ⑤ ダウンタイムPareto(区分)⑥ 設備別ダウンタイム
""")

w("""## 7. 適応型データ取り込み(任意フォーマット対応)

固定スキーマに縛らず、**どんな形式でも入口で吸収**する設計。役割分担は「**判断はAI、適用はコード、辞書は時短**」。

`profile_map.py <file...>` が:
1. 構造解析(シート/列/サンプル/行数)。複数ファイル(CSV/Excel/TXT混在)・TXTの区切り自動判定に対応。
2. 列を標準概念へ自動マッピング(別名・表記ゆれ吸収。例:号機→設備、型式→機種、出来高台数→実績数)。信頼度(高/中)。短い英字略語(ct/ok/ng)は英字ラン完全一致のみで誤爆防止。
3. **今できる分析**と**あると良いデータ→できる分析**を提示(ケイパビリティマップ)。
4. 低信頼/未マップの項目だけユーザーに質問(全列は聞かない)。

検証済み: フル19シートExcel=14分析すべて可・確認4項目のみ / 汚しCSV=号機等を吸収・不足を明示 / txt=区切り自動判定 / シート不足xlsx=落ちずに不足を提示。

**値レベルの紐づけ(ライン名↔ラインコード等)**は、設備マスタ(拠点-ライン-工程-設備の名称↔コード)を正の対応表(crosswalk)として使えば解決可能。マスタが網羅・最新であることが前提。未知の呼び名はAIが文脈で当てて確認→マスタに別名追記(運用で育てる)。標準概念と別名・必要データは `field-dictionary.md` 参照。
""")

w("""## 8. オンプレOracle ライブ連携

クラウド側からは社内Oracleに直接届かない。**Oracleに到達できる端末(社内PC。Desktop Commander経由でClaudeから起動可)で抽出を実行**し、結果を診断に渡す。

### 8.1 流れ
1. Claudeに日本語で指示(例「今日のL-01の稼働を診断して」)。
2. Claude → Desktop Commander → 端末で `oracle_pull.py` 実行 → python-oracledb(thinモード)でライブ接続(資格情報は端末の環境変数)→ 最新行をCSV出力。
3. 大量データは端末で `diagnose.py` まで回し**要約をClaudeへ**返す(重い処理はコード、判断はAI)。
4. Claudeが解釈し、いつ→どこ→何が→なぜ→対策。

### 8.2 セキュリティ
- 読み取り専用・最小権限アカウント。抽出はオンプレ実行。PWは環境変数 or ウォレット(チャット/クラウド/ファイルに書かない)。必要列のみSELECT。
- 資格情報の扱いは「環境変数に置く」を採用(ORA_USER/ORA_PASSWORD/ORA_DSN)。

### 8.3 リアルタイム性
- SQLの `WHERE 日付 >= TRUNC(SYSDATE)-N` や `>= SYSDATE-1` で現在時刻基準。実行ごとに最新。必要なら短間隔再実行/スケジュール化。

### 8.4 スキーマ把握(初回1回)
- `user_tables` / `user_tab_columns` で構造を取得 → Claudeが実列を標準概念にマッピング(profile_mapの考え方)→ 曖昧のみ質問 → スキーママップ/実名版SQLをファイル保存。以降は日本語指示だけで回る。スキーマ変更時のみ更新。
- 詳細手順・SQL雛形は `oracle-connection.md` / `extract_template.sql`(4.2に全文)。
""")

w("""## 9. 運用手順(日本語指示→診断)

1. **入口**: ファイルなら `profile_map.py` で構造把握、Oracleなら `oracle_pull.py` でライブ抽出。
2. **確認**: 低信頼の概念だけユーザーに確認(「出来高台数は実績数でよいですか?」)。
3. **指標算出**: テンプレ形式なら `diagnose.py` で計画/実績・OEE・ダウンタイムPareto・機種ズレ・悪化起点。
4. **診断**: 固定フロー(いつ→どこ→何が→なぜ→対策)。OEE主因→4Mの当たり→RCAへ。
5. **展開**: 慢性はbad-actor、対策はFMEA/PM最適化、最後に標準化(発生防止+流出防止)。

指示はすべて日本語でよい。Claudeが必要データを判断しSQL/解析を自動生成する(そのために初回のスキーマ把握が前提)。
""")

w("""## 10. 今後の拡張候補
- 予兆・予防(P-F/Weibull): 同じMITリポジトリから pf-interval-sizing / failure-pattern(Weibull)を取り込み、センサ振動・寿命データで「壊れる前に」。
- トレーサビリティ強化: シリアルへ治具No・作業者IDを付与し4M完全追跡。
- 環境/エネルギー/受注データの追加で分析の幅を拡張。
- 値レベル紐づけ(設備マスタcrosswalk)の実装で、ライン名バラバラの生データも自動でコード整合。
""")

w("""## 11. 付録: 再現スクリプト

シミュレーションデータの再現用(セッション内のパスを含むため、流用時はパスを調整)。""")
embed("gen_sim3.py(データ生成・離散イベントシミュレーション)", "gen_sim3.py","python")
embed("build_all3.py(19シートExcel構築・OEE計算式)", "build_all3.py","python")

w("""## 12. 付録: インストール時のトラブル

- 症状: プラグイン保存時 `[remoteMarketplaceClient] transport error: net::ERR_CONNECTION_TIMED_OUT`。
- 原因: **ネット未接続**(マーケットプレイス同期サービスへ到達できずタイムアウト)。プラグインファイル自体は正常。
- 対処: ネット接続して再実行。再接続後も出る場合はVPN/プロキシ/ファイアウォール、アプリ再起動、組織のネットワーク設定を確認。
""")


w("""## 13. 付録: 信頼性スキル集(18スキル)の評価(検討の出発点)

対象: `Rob-Reliability/reliability-skills-for-claude`(著者 Joss Bohler、MIT)。18スキル/6ドメイン。
位置づけ: **装置産業・資産集約型の設備保全(plant reliability)向け**であり、ディスクリート量産のラインバランス/ボトルネックとは別物。

| 観点 | 評価 | 要点 |
|---|---|---|
| 方法論の正統性 | ◎ | IEC60812/SAE J1739/ISO14224、RCM(SAE JA1011/JA1012)、Nowlan&Heap を正確に運用。侵襲的保全が初期故障を誘発する論点まで含む。 |
| スキル設計の完成度 | ◎ | frontmatter→When→Field-Grade→Workflow→Output→Quality Bar→Example の統一構造。 |
| ハルシネーション対策 | ◎ | 証拠階層(現場>OEM>判断>AI)、Confidenceラベル、"approved/audit-readyと言うな"。 |
| 装置産業への適合 | ◎ | ポンプ・ファン・定修など連続/装置産業に最適。 |
| ディスクリート量産への適合 | △ | TPM/工程内不良/ライン能率の文脈とは半分しか重ならない。 |
| データ前提の重さ | ○ | CMMS履歴・FMEA・OEM等の入力が必要。叩き台アクセラレータ。 |
| システム統合・自動化 | △ | ライブ連携なし・プラグイン化されていない単独md・英語のみ。 |
| 日本語/現地化 | △ | 和訳・現地語彙(保全/定修/不適合)調整が要る。 |

結論: 装置産業の信頼性業務では現状ベスト級。ただし量産組立の品質保全用途やCMMS連携・日本語運用には作り込みが要る、という性格。
本セッションでは、この集合から **RCA/bad-actor/FMEA/PM最適化の4スキルを取り込み**、ディスクリート診断の核(production-scheduling)と新規診断スキルに統合した。
""")

w("""## 14. 付録: production-scheduling 選定の経緯

1. コネクタ・スキルのレジストリ検索 → クラウドDB(Supabase/PlanetScale/MotherDuck等)はあるが**ライン診断の該当スキルは無し**。
2. コミュニティGitHub探索で候補を抽出:
   - **production-scheduling**(affaan-m/everything-claude-code ほか多数フォーク。最人気フォークは21万超の共有、Apache-2.0)= 本命。
     ボトルネック(TOC/DBR)、ラインバランス、SMED、OEE、外乱対応、ERP/MES連携を網羅。ただし**知識・役割プロンプト型**で計算ツールは同梱せず。
   - **process-mapper**(alirezarezvani/claude-skills の business-operations)= 次点。BPMNスイムレーン+ボトルネック検知+サイクルタイム/VA%、決定論Python付き。ただし業務プロセス汎用寄り。
   - operations-manager / process-quality-optimization / kaizen(mcpmarket)= 汎用オペ改善。ライン特化度は低。
3. 決定: **production-scheduling を核に採用**(ディスクリート/バッチ組立に最適、出典明確・Apache-2.0)。不足する「可視化+自動診断+日本式フレーム」は新規 production-drop-diagnosis で補完。
""")

w("""## 15. 付録: テストデータ検証(別フォーマット適応)

profile_map を3パターンで検証し、いずれも適応を確認した。
- **A: 複数CSV(英語/日本語混在)** — A_production.csv + A_downtime.csv を2ファイル一括。PlanQty→計画数、設備名→設備 等を吸収、8分析が「今できる」。
- **B: txt(タブ区切り)** — 区切り自動判定。号機→設備、事象→停止理由。停止データのみのため「今できる=ダウンタイム分析」。
- **C: xlsx シート不足&別列名** — 生産記録+不良票のみ(計画・停止なし)。「今できる=まだ無し」とし各分析の不足概念を列挙(落ちずに案内)。
途中で英語短略語(\"ActualQty\"の\"ct\")の誤マッチを発見し、短い英字略語は英字ラン完全一致のみに修正。
""")
embed("testdata/A_production.csv", "testdata/A_production.csv","text")
embed("testdata/A_downtime.csv", "testdata/A_downtime.csv","text")
embed("testdata/B_stop_log.txt", "testdata/B_stop_log.txt","text")

w("""## 16. 付録: ダッシュボード生成スクリプト

`build_dashboard.py` で `_simdata3.json` から `_dash.json`(三角図/PPH/流動数/ダウンタイム/OEE推移/KPI)を生成し、
HTMLテンプレートに `__DATA__` として差し込んで `製造ライン診断ダッシュボード.html` を再生成する。""")
embed("build_dashboard.py", "build_dashboard.py","python")


w("""## 17. 付録: 隣接領域の連携(生産計画・人員配置・在庫管理)

「生産が落ちた原因」だけでなく、生産計画・人員・在庫を**連携して把握**できるか、の検討結果。

### 17.1 現状の充足
- 生産計画: production-scheduling(導入済み)が 需要→MPS→MRP→工程展開→順序付け→MES の流れを扱う。
- 人員配置: 同スキルが労務を制約として扱う(スキルマトリクス・シフトパターン・クロストレーニングROI)。
- データ面: 計画シート(生産計画)・作業者割当(人員)・材料ロット/投入(在庫の入口)が既に存在。

### 17.2 取り込み候補
- 在庫管理 → inventory-demand-planning(everything-claude-code系。需要予測・安全在庫・補充・販促リフト)。production-schedulingの姉妹スキルで相性良。在庫本体の最有力。
- 統合型「Inventory & Supply Chain Manager」系(在庫+需要+仕入先+SCM)。
- 人員(業務寄り)→ operations:capacity-plan(負荷分析・稼働予測・採用/優先度)。工場シフト特化の専用スキルは見当たらず、必要なら自作。

### 17.3 連携の仕組み
これらは通常ERP/APSの別モジュールだが、連携の本質はClaudeが各データを束ねて突合すること。Oracleライブ連携(または各ファイル)で 生産計画・人員割当・在庫/材料 を取得し、field-dictionary/profile_map に在庫・人員・計画の概念を足せば、一つの診断ビューで「計画 vs 実績(達成率)」「人員 vs 必要工数(過不足)」「在庫 vs 消費(欠品/滞留)」を一望できる。例: 在庫が切れそう→計画と人員を見て段取りを組み替える、まで拡張可能。
""")

w("""## 18. 付録: 人員配置最適化(配置最適)

スキルマップ + 配置ルールがあれば、配置最適化(割当問題)として解ける。

### 18.1 入力
- スキルマップ: 作業者 × 工程/設備 × 習熟度(○/△/× or レベル1-3)。作業者割当の認定レベル(熟練/認定/訓練中)が出発点。
- 工程要件: 必要人数、必要スキルレベル。  可用性: 出勤/シフト/休暇。  配置ルール(下記2層)。

### 18.2 ルールは2層
- ハード制約(必ず守る): 認定がない工程に配置不可、安全/法規(有資格者必須)、1人=1持ち場、各工程のカバレッジ充足。
- ソフト目的(なるべく良く): 「みな同じくらい」=負荷の平準化(負荷率の差/分散を最小化、または最大負荷を最小化)。熟練をボトルネック工程へ、新人は熟練とペア(育成)、クロストレーニング促進 等。

### 18.3 方法
割当問題/整数計画(PuLP・OR-Tools・scipy)で、ハード制約を満たしつつソフト目的を最適化。役割分担は「計算はソルバー(コード)、ルール設計と例外判断はAI」。

### 18.4 注意点
- 多目的(平準化 vs 熟練を制約工程 vs 育成)はトレードオフ。優先順位/重みをユーザーが決める。
- 制約衝突で解なしの時は緩和案(残業/応援/カバレッジ緩和)を提示。
- 品質はスキルマップの鮮度に依存。
""")

doc="\n".join(out)
open("製造ライン診断_セッション完全記録.md","w",encoding="utf-8").write(doc)
print("written 製造ライン診断_セッション完全記録.md")
print("chars",len(doc),"approx lines",doc.count(chr(10)))
