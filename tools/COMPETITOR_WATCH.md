# 競合アプリ更新ウォッチャー セットアップ手順

毎週**月曜18時(日本時間)** に、競合アプリ（App Store）の仕様更新を自動チェックし、
変化があれば **Claudeが自社への示唆を分析してメール送信** する仕組みです。

- 実行場所: GitHub Actions（あなたのPCを起動しなくても動きます）
- データ取得: iTunes Lookup API（公式・無料・スクレイピング不要）
- 関連ファイル:
  - `.github/workflows/competitor-watch.yml` … 実行スケジュール
  - `tools/competitor_watch.py` … 本体スクリプト
  - `tools/competitors.json` … 監視対象アプリの設定
  - `tools/competitor_snapshot.json` … 前回チェック結果（自動更新）

---

## 1. 必要なシークレットを4つ登録する

GitHub のリポジトリページで:
**Settings → Secrets and variables → Actions → 「New repository secret」**
を開き、以下の4つを1つずつ登録します（名前は完全一致で）。

| シークレット名 | 中身 | 取得方法 |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude の APIキー | https://console.anthropic.com → API Keys で発行 |
| `MAIL_USERNAME` | 送信元の Gmail アドレス | 例: `youraddress@gmail.com` |
| `MAIL_PASSWORD` | Gmail の「アプリパスワード」 | 下記参照（通常のログインPWではない） |
| `MAIL_TO` | レポートの受信先アドレス | 自分の受け取りたいメールアドレス |

### Gmailアプリパスワードの作り方
1. 送信に使うGoogleアカウントで **2段階認証を有効化**
2. https://myaccount.google.com/apppasswords を開く
3. 適当な名前（例: competitor-watch）で作成 → 表示された16桁を `MAIL_PASSWORD` に登録

> 会社ドメイン(@netdreamers.co.jp)がGoogle Workspaceならそのアドレスでも可。
> 難しければ送信専用に個人Gmailを使い、`MAIL_TO` を会社アドレスにすればOK。

---

## 2. 動作テスト（手動実行）

GitHub のリポジトリページで:
**Actions タブ → 左の「competitor-watch」→ 右上「Run workflow」**
を押すと、その場で実行できます。

- 初回はベースライン（基準値）を作るだけでメールは飛びません
- 2回目以降、前回から変化があった時だけメールが届きます
- テストでメールを飛ばしたい場合は `tools/competitor_snapshot.json` の
  どれかの `version` を古い値に書き換えてからコミット → Run workflow

---

## 3. 監視対象を増やす・減らす

`tools/competitors.json` の `competitors` 配列を編集します。
`id` は App Store の URL `.../id6761375438` の数字部分です。

```json
{ "id": "6761375438", "label": "アプリ名" }
```

`your_app.summary` を自社アプリの最新の機能に合わせて更新しておくと、
Claudeの分析がより的確になります。

---

## 仕組みの補足
- 変化が検知された時のみ `competitor_snapshot.json` が更新コミットされます
  （= 競合がアップデートした週だけ、リポジトリに1コミット入ります）
- GitHub Actions の定期実行は混雑時に数分〜十数分遅れることがあります
- メール本文の `report.html` は実行のたびに生成される一時ファイルです（gitignore済み）
