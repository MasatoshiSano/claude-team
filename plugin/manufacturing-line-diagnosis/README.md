# Manufacturing Line Diagnosis

製造ラインの「生産数が落ちている・稼働率が悪い、なぜか」を、データから順序立てて切り分けるためのスキル集です。核2スキル + 補完3スキルを束ねています。

## 含まれるスキル

### 核(Core)
- **production-scheduling** — ライン診断の頭脳。ボトルネック(TOC / Drum-Buffer-Rope)、ラインバランス、段取り最適化(SMED)、OEE、外乱対応、ERP/MES連携。
- **root-cause-analysis-copilot** — 構造化RCA。証拠ゲート(Verified / Hypothesis / Refuted)、物理→人→潜在の深掘り、「人のミスで止めない」作法。

### 補完(Complementary)
- **bad-actor-analysis** — CMMS履歴から慢性的に足を引っ張る設備/工程をPareto特定し、RCA候補を優先順位づけ。
- **fmea-generation** — ワークショップ用のFMEA/FMECAドラフト生成(IEC 60812 / SAE J1739 / ISO 14224)。
- **pm-optimization** — 故障モードに紐づかない「形骸化PM」を洗い出すPM見直し。

## 推奨の使い方(原因特定フロー)

製造三角図/流動数曲線で「いつ・どこで落ちたか」→ **production-scheduling** の OEE分解(可用性×性能×品質)で「何が落ちたか」→ 分岐(ダウンタイム/サイクルタイム/不良)→ **root-cause-analysis-copilot** で「なぜか」→ 対策・標準化。慢性不具合は **bad-actor-analysis** で裏取り、対策は **fmea-generation / pm-optimization** へ展開。

## 出典とライセンス

各スキルは外部のコミュニティ作品を取り込んだものです。原作者と原ライセンスに従います。

- production-scheduling: from `affaan-m/everything-claude-code` (author: evos) — **Apache-2.0**
- root-cause-analysis-copilot / bad-actor-analysis / fmea-generation / pm-optimization: from `Rob-Reliability/reliability-skills-for-claude` (author: Joss Bohler / Rob Reliability) — **MIT**

本バンドルは上記を再パッケージしたもので、各スキル本文は原典を尊重しています。商用標準団体・ベンダーとは無関係(独立・非公式)。

## v0.2.0 追加: production-drop-diagnosis(診断スキル)

生産数低下・稼働率悪化の原因を「いつ→どこ→何が→なぜ→対策」の固定フローで切り分ける6スキル目。
製造三角図・流動数曲線・計画/実績PPH(時間×機種)・OEE分解・ダウンタイムParetoで現象を特定し、
4Mと発生/流出でRCA(root-cause-analysis-copilot)へ橋渡しする。
`scripts/diagnose.py <xlsx>` でライン診断Excelを読み、計画/実績・OEE(A/P/Q)・ダウンタイムPareto・機種ズレ・悪化起点を自動算出。

## v0.3.0: 適応型データ取り込み(任意フォーマット対応)

production-drop-diagnosis に `scripts/profile_map.py` を追加。任意のExcel/CSVを解析し、列を標準概念へ自動マッピング(別名・表記ゆれを吸収)、「今できる分析」と「あると良いデータ→できる分析」を提示、低信頼の項目だけユーザーに質問する。固定スキーマに縛られず、どんな形式でも入口で吸収する。対応表は `references/field-dictionary.md`。

## v0.3.1: profile_map を複数ファイル/txt対応・誤マッチ修正

profile_map.py が複数ファイル(CSV/Excel/TXT混在)を一括解析できるように拡張。TXT/TSVは区切りを自動判定。
英字の短い略語(ct/ok/ng等)の部分一致誤爆を修正(英字ラン完全一致のみ)。シート不足・別列名・多ファイルでも、
できること/あるとできること/確認したい項目を提示する。

## v0.4.0: オンプレOracle ライブ取得

production-drop-diagnosis に `scripts/oracle_pull.py`(python-oracledb thinモード・資格情報は環境変数)、
`references/oracle-connection.md`(接続手順・セキュリティ)、`references/extract_template.sql`(列を標準概念名にエイリアスした抽出雛形)を追加。
クラウドから直接は届かないオンプレOracleでも、到達できる端末(Desktop Commander経由可)でライブ抽出→診断に渡せる。
WHERE SYSDATE基準でリアルタイム。PWはチャット/クラウドに出さない。

## v0.4.1: diagnose.py に計画/実績PPH(時間別)分析を追加

diagnose.py が 時間別PPH シートを読み、日別に「PPH不足時間数(実績PPH<計画PPHの8割)・機種ズレ時間数・最悪時間/最大差」を自動算出。
PPH計画/実績が決定論ツールの出力でも一級の材料になった(従来は読み筋のみ)。
