# session-2026-06-20

2026-06-20 の Claude セッションで作成した、業務診断・スキル・CI雛形・ロードマップ一式。
このフォルダ内で完結しており、リポジトリ直下の既存ファイルとは独立している。

## 読む順番
1. docs/session-record.md — セッション完全記録（全19章）。ここから読む。
2. docs/diagnosis-roadmap.html — 業務診断と全体ロードマップ（1枚・ブラウザで開く）。

## 構成
- docs/        記録とロードマップ
- skills/reliability/   設備保全4スキル（rca-copilot / bad-actor-analysis / fmea-generation / cmms-data-analysis, MIT）
- skills/aws-deploy/    AWS系デプロイ品質ゲート（7ゲート）
- skills/daily-report/  日報→TaskFlow記録（たたき台）
- ci/          AWS系7ゲートの Gitea Actions ワークフロー雛形

## 重要な注意
- 無人自動化で `claude -p` を使わない（API課金になる。記録 §18-8）。Cowork のスケジュールタスクで Cowork 自身が回す構成を推奨。
- 記録には設備名・システム名・プロキシ情報など社内情報を含む。プライベートリポジトリであることを確認すること。
- 各スキル・雛形は実環境に合わせた差し替えが前提のたたき台（検討・設計フェーズ）。
