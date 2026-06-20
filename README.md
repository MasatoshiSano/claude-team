# claude-team — 製造ライン診断

製造業の「生産数低下・稼働率悪化の原因特定」を、データから固定フロー(製造三角図→流動数曲線→PPH→OEE→ダウンタイム→RCA)で切り分けるための一式。Cowork/Claude Code プラグイン、整合性検証済みのシミュレーションデータ、診断ダッシュボード、完全記録ドキュメントを収録。

## 構成
```
plugin/
  manufacturing-line-diagnosis.plugin        … インストール用パッケージ(zip)
  manufacturing-line-diagnosis/              … 同内容のソース(GitHubで閲覧用)
    .claude-plugin/plugin.json
    skills/
      production-drop-diagnosis/             … 新規: 生産数低下 原因特定(scripts/ + references/)
      production-scheduling/                 … 取り込み(Apache-2.0)
      root-cause-analysis-copilot/           … 取り込み(MIT)
      bad-actor-analysis/                    … 取り込み(MIT)
      fmea-generation/                       … 取り込み(MIT)
      pm-optimization/                       … 取り込み(MIT)
docs/
  製造ライン診断_セッション完全記録.md         … 方法論・全ファイル全文・データ設計・運用・Oracle連携(全18章)
data/
  manufacturing-line-sim-data.xlsx           … 19シート・整合性保証のシミュレーションデータ
  testdata/                                  … 別フォーマット適応テスト(複数CSV/txt/シート不足)
dashboard/
  製造ライン診断ダッシュボード.html            … データ内蔵・再オープン可
scripts/
  gen_sim3.py / build_all3.py / build_dashboard.py / build_doc.py … 再現用
```

## 使い方(概要)
1. `plugin/manufacturing-line-diagnosis.plugin` を Cowork/Claude Code に取り込む。
2. ライン診断データ(Excel/CSV/TXT、または Oracle ライブ)を渡す。
3. `production-drop-diagnosis` が profile_map で構造把握→diagnose で指標算出→「いつ→どこ→何が→なぜ→対策」で診断。
詳細は `docs/製造ライン診断_セッション完全記録.md`。

## ライセンス
- production-scheduling: Apache-2.0(affaan-m/everything-claude-code)
- その他の取り込みスキル: MIT(Rob-Reliability/reliability-skills-for-claude)
- 新規作成物(production-drop-diagnosis、データ、ダッシュボード、ドキュメント): MIT
各スキルの出典は plugin/.../README.md を参照。
