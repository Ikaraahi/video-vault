# Video Vault — GitHub Pages版

完全無料・クレカ不要・厳重セキュリティの動画視聴システム。
動画をAES-256で暗号化してGitHub Pagesで配信、ブラウザ内で復号して再生する仕組み。

事業: 全社
状態: 開発中
作成日: 2026-05-10

---

## 🎯 特徴

- ✅ **完全無料**（GitHub Pages無料枠）
- ✅ **クレカ登録一切不要**
- ✅ **AES-256-GCM 暗号化**（軍事レベル）
- ✅ **PBKDF2 鍵導出**（10万回反復、ブルートフォース耐性）
- ✅ リポジトリが公開でも安全（鍵がないと再生不可）
- ✅ 課金リスクゼロ（GitHubが無料枠を超えても課金されない）

---

## 🔐 セキュリティの仕組み

```
[管理者]
  動画ファイル + パスワード
        ↓ encrypt.html で暗号化
  videos/vid001.enc（AES-256-GCM暗号化済）
        ↓ GitHubにpush

[GitHub Pages]
  index.html + manifest.json + videos/*.enc を配信

[視聴者]
  https://USER.github.io/REPO/?id=vid001
        ↓ パスワード入力
  ブラウザ内で PBKDF2 → 鍵生成 → AES復号
        ↓
  Blob URLで <video> 再生
```

### 攻撃耐性

| シナリオ | 結果 |
|---|---|
| 視聴URLが流出 | ✅ パスがないと暗号化動画は再生不可 |
| 暗号化動画ファイル(.enc)が流出 | ✅ パスがないと復号できない |
| パスワードがブルートフォース | ⚠️ 100,000回反復で1パス試行に約100ms。長いパスを推奨 |
| ソースコードが見られる | ✅ 公開前提。鍵情報は含まれない |
| 視聴中の画面録画 | ⚠️ 防御不可（どの方式でも同じ） |

---

## 📁 ファイル構成

```
動画パスワード保護_GitHub/
├── README.md         ← このファイル
├── index.html        ← 視聴ページ（パス入力＋復号＋再生）
├── encrypt.html      ← 暗号化ツール（ブラウザでD&D）
├── manifest.json     ← 動画一覧メタデータ
└── videos/
    └── *.enc         ← 暗号化済み動画ファイル
```

---

## 🚀 セットアップ手順

### Step 1: GitHubアカウント＆リポジトリ作成

1. https://github.com/ でアカウント作成（無料、クレカ不要）
2. ログイン後、右上「+」→「New repository」
3. 設定:
   - Repository name: `video-vault`（任意）
   - **Public** を選択（暗号化されてるので公開でOK）
   - 「Add a README file」にチェック
4. 「Create repository」

### Step 2: ファイルをアップロード

このフォルダ（`動画パスワード保護_GitHub/`）の中身を全てGitHubリポジトリに上げる。

**手軽な方法（ブラウザでD&D）**:
1. 作成したリポジトリ画面の「Add file」→「Upload files」
2. 以下をD&D:
   - `index.html`
   - `encrypt.html`
   - `manifest.json`
   - `videos/` フォルダごと（中身は `.gitkeep` だけでOK）
3. 「Commit changes」

**コマンドラインで（gitに慣れてるなら）**:
```bash
cd "07_プロジェクト管理/動画パスワード保護_GitHub"
git init
git remote add origin https://github.com/YOUR_USER/video-vault.git
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

### Step 3: GitHub Pagesを有効化

1. リポジトリ画面の「Settings」タブ
2. 左メニュー「Pages」
3. 「Source」: `Deploy from a branch`
4. Branch: `main` / `/ (root)`
5. 「Save」をクリック
6. 数分待つと `https://YOUR_USER.github.io/video-vault/` が公開される

### Step 4: 動作確認

1. ブラウザで `https://YOUR_USER.github.io/video-vault/encrypt.html` を開く
2. 暗号化ツールが表示されればセットアップ完了

---

## 🎬 動画の追加（運用フロー）

### Step A: 動画を圧縮（100MB以下にする）

GitHub単一ファイル制限は**100MB**。元動画が大きい場合は圧縮：

```bash
# ffmpegで圧縮（事前にbrew install ffmpegでインストール）
ffmpeg -i 元動画.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k -movflags +faststart 出力.mp4
```

| 動画長 | ビットレート目安 | 想定サイズ |
|---|---|---|
| 5分 | 1.5 Mbps | 〜60 MB |
| 10分 | 1.0 Mbps | 〜80 MB |
| 15分 | 0.8 Mbps | 〜95 MB |

サイズが超える場合は `-crf 30` や `-crf 32` で更に圧縮可能（数値が大きいほど低画質）。

### Step B: 暗号化

1. `https://YOUR_USER.github.io/video-vault/encrypt.html` を開く
2. 「動画情報」を入力:
   - 動画ID: `vid001`（半角英数）
   - タイトル: `商品紹介動画A`
   - パスワード: `任意の文字列`（強めに推奨）
   - 有効期限: 任意
3. 動画ファイルをドラッグ＆ドロップ
4. 「暗号化を開始」ボタン
5. 完了後:
   - 「.enc ファイルをDL」を押してDL
   - 「JSONをコピー」を押す

### Step C: GitHubに反映

1. リポジトリ画面の `videos/` フォルダを開く
2. 「Add file」→「Upload files」→ DLした `.enc` ファイルをアップ
3. リポジトリ画面の `manifest.json` を開く → 編集（鉛筆アイコン）
4. `"videos": [` の中にコピーしたJSONを追加:
```json
{
  "videos": [
    {
      "id": "vid001",
      "title": "商品紹介動画A",
      "file": "videos/vid001.enc",
      "salt": "...",
      "iv": "...",
      "contentType": "video/mp4",
      "expiresAt": null,
      "createdAt": "2026-05-10"
    }
  ]
}
```

> ⚠️ 2本目以降を追加する場合は **配列内の要素間にカンマ** を忘れずに：
> ```json
> "videos": [
>   { ... vid001 ... },
>   { ... vid002 ... }
> ]
> ```

5. 「Commit changes」

### Step D: スプシに視聴URLを記載

1〜2分後にGitHub Pagesに反映される。視聴URL：
```
https://YOUR_USER.github.io/video-vault/?id=vid001
```

スプシに貼って配布：
```
タイトル          | 視聴URL                                              | パスワード
商品紹介動画A     | https://USER.github.io/video-vault/?id=vid001        | hello123
```

---

## 🔄 動画の更新・削除

### パスワード変更
動画を **再度 encrypt.html で暗号化** してアップロード（同じ動画IDで上書き）。
manifest.json も新しいSalt/IVに置き換える。

### 削除
1. `videos/` から該当 `.enc` ファイルを削除
2. `manifest.json` から該当エントリを削除
3. コミット

### 期限変更
`manifest.json` の `expiresAt` を編集してコミット。

---

## ⚠️ 制約・注意点

### 動画サイズ
- **GitHub単一ファイル50MB推奨、100MB上限**（通常Git）
- 超えたい場合は **Git LFS** を有効化（月1GB帯域まで無料、超えると有料）
- 短尺動画（5〜15分）なら圧縮で収まる

### 再生時の体感
- 視聴者が動画を**全部DLしてから復号**するため、ストリーミング再生不可
- 50MB動画 → 復号約3〜8秒
- 100MB動画 → 約8〜20秒（回線次第）
- 一度復号したらシーク・スキップは普通通り

### 視聴履歴・ログ
- GitHub Pagesは静的配信のため、**視聴ログは取得不可**
- ログが必要なら GAS版 / R2版 を検討

### リポジトリの公開について
- Public 推奨（無料、Pages使える）
- 公開されても暗号化されてるので動画は再生不可
- ただし、**動画のメタ情報（タイトル等）は manifest.json で公開**される
- 機密タイトルがある場合は伏せ字にする運用も可

---

## 🆘 トラブルシュート

### 「manifest.json not found」
- GitHub Pagesが反映されるまで数分かかる
- リポジトリのトップに manifest.json が置いてあるか確認

### 「パスワードが違います」
- パスワードのスペルミス確認
- encrypt.html で生成したSalt/IVが正しくmanifest.jsonに反映されてるか確認
- 暗号化時と視聴時で動画ファイルが一致してるか

### 暗号化が止まる
- 動画サイズが大きすぎる可能性（500MB超だとブラウザがメモリ不足になる）
- まず ffmpeg で圧縮してから暗号化

### 再生が始まらない
- ブラウザDevToolsのConsoleでエラー確認
- video/mp4 対応形式か確認（H.264/AAC推奨）

---

## 🛡 セキュリティ強化（オプション）

### 強いパスワードの推奨
- 12文字以上、英大小数字記号混在
- 推測されにくいフレーズ
- 動画ごとに別パス

### 視聴期限の活用
manifest.json の `expiresAt` で日付指定。期限切れ後はパス入力すら通らなくなる。

### 動画への透かし
動画作成時に視聴者識別コードを入れる（漏洩追跡用）。配布相手ごとに別動画を暗号化する運用。
