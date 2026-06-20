# GitHub への push 手順(あなたの端末で1回だけ)

このフォルダ(claude-team)を https://github.com/MasatoshiSano/claude-team.git に上げる手順です。
認証(ユーザー名 + Personal Access Token、または SSH)はあなたの端末で行ってください。

## 初回(リポジトリが空の場合)
```bash
cd path/to/claude-team
git init
git add .
git commit -m "製造ライン診断: プラグイン・シミュレーションデータ・ダッシュボード・完全記録"
git branch -M main
git remote add origin https://github.com/MasatoshiSano/claude-team.git
git push -u origin main
```

## 既にリポジトリに中身がある場合
```bash
cd path/to/claude-team
git init
git remote add origin https://github.com/MasatoshiSano/claude-team.git
git add .
git commit -m "製造ライン診断 一式を追加"
git pull --rebase origin main   # 既存履歴を取り込む
git push -u origin main
```

## 認証メモ
- HTTPS の場合、push 時にユーザー名と Personal Access Token(パスワード欄にトークン)を求められます。
- うまくいかない時は SSH リモート(git@github.com:MasatoshiSano/claude-team.git)も検討してください。
