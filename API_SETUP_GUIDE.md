# 🔑 API取得ガイド

このワークフローで必要な各APIの取得方法を詳しく解説します。

## 📋 必要なAPI一覧

| API | 用途 | 必須度 | 取得難易度 |
|-----|------|--------|----------|
| Zoom API (JWT) | 録画情報取得 | ✅ 必須 | ⭐⭐ 中 |
| OpenAI API | GPT-5コンテンツ生成 | ✅ 必須 | ⭐ 易 |
| Discord Webhook | Discord投稿 | ✅ 必須 | ⭐ 易 |
| GitHub Token | repository_dispatch | ⚠️ 推奨 | ⭐ 易 |

---

## 1️⃣ Zoom API (JWT) の取得方法

### 📍 概要

Zoom APIを使用して録画情報を取得するために、JWT認証方式のアプリを作成します。

### 🔗 公式リンク

- **Zoom App Marketplace**: https://marketplace.zoom.us/
- **JWT App作成ガイド**: https://marketplace.zoom.us/docs/guides/build/jwt-app

### 📝 手順

#### ステップ1: Zoom App Marketplaceにアクセス

1. https://marketplace.zoom.us/ にアクセス
2. Zoomアカウントでログイン
3. 右上の「**Develop**」→「**Build App**」をクリック

#### ステップ2: JWT App を作成

1. アプリタイプ選択画面で「**JWT**」を選択
2. 「**Create**」をクリック

> ⚠️ **注意**: 2023年以降、ZoomはJWT認証を非推奨としています。本番環境では**Server-to-Server OAuth**への移行を推奨します。

#### ステップ3: 基本情報を入力

以下の情報を入力します：

- **App Name**: 任意（例: "Zoom to Discord Automation"）
- **Short Description**: アプリの簡単な説明
- **Company Name**: 会社名または個人名
- **Developer Contact**: メールアドレス

「**Continue**」をクリックして次へ。

#### ステップ4: API認証情報を取得

「**App Credentials**」セクションで以下の情報を確認・コピーします：

```plaintext
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API Secret: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

この2つの値をメモ帳などに保存してください。

#### ステップ5: 機能を有効化

「**Feature**」タブに移動し、必要に応じて以下を有効化：

- **Event Subscriptions**: Webhook通知を受け取る場合（後述）

#### ステップ6: アプリを有効化

「**Activation**」タブで「**Activate your app**」をクリックしてアプリを有効化します。

### ✅ 確認事項

- [ ] API Key を取得した
- [ ] API Secret を取得した
- [ ] アプリを有効化した

### 🎯 GitHub Secretsに設定

```yaml
ZOOM_API_KEY: <取得したAPI Key>
ZOOM_API_SECRET: <取得したAPI Secret>
```

---

## 2️⃣ OpenAI API キーの取得方法

### 📍 概要

GPT-5を使用するためのOpenAI APIキーを取得します。

### 🔗 公式リンク

- **OpenAI Platform**: https://platform.openai.com/
- **APIキー管理**: https://platform.openai.com/api-keys

### 📝 手順

#### ステップ1: OpenAI Platformにアクセス

1. https://platform.openai.com/ にアクセス
2. OpenAIアカウントでログイン（未登録の場合は新規登録）

#### ステップ2: APIキーを作成

1. 左サイドバーから「**API keys**」をクリック
2. 「**+ Create new secret key**」をクリック
3. キー名を入力（例: "Zoom Discord Workflow"）
4. 権限を選択（デフォルトでOK）
5. 「**Create secret key**」をクリック

#### ステップ3: APIキーをコピー

```plaintext
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **重要**: このキーは一度しか表示されません。必ず安全な場所に保存してください。

### 💰 料金と利用枠

#### GPT-5 料金（2025年1月時点）

- **入力**: $1.25 / 1M トークン
- **出力**: $10.00 / 1M トークン

#### 使用量目安

1回の実行あたり：
- 入力: 約500トークン（$0.000625）
- 出力: 約300トークン（$0.003）
- **合計: 約$0.004 / 回**

月100回実行で約$0.40です。

#### 課金設定

1. 左サイドバーから「**Settings**」→「**Billing**」
2. クレジットカードを登録
3. 使用量上限を設定（推奨: $10/月）

### 🔍 GPT-5アクセス権限の確認

GPT-5は段階的にロールアウトされています。以下で確認できます：

1. **Playground**にアクセス: https://platform.openai.com/playground
2. モデル選択ドロップダウンに「**gpt-5**」が表示されるか確認

表示されない場合:
- GPT-5はまだ利用できません
- 代替として「**gpt-4**」または「**gpt-4-turbo**」を使用してください

### ✅ 確認事項

- [ ] APIキーを取得した
- [ ] 課金設定を完了した
- [ ] GPT-5またはGPT-4へのアクセスを確認した

### 🎯 GitHub Secretsに設定

```yaml
OPENAI_API_KEY: <取得したAPIキー>
```

---

## 3️⃣ Discord Webhook URLの取得方法

### 📍 概要

Discordの特定チャンネルにメッセージを投稿するためのWebhook URLを取得します。

### 🔗 公式リンク

- **Discord**: https://discord.com/
- **Webhook公式ドキュメント**: https://discord.com/developers/docs/resources/webhook

### 📝 手順

#### ステップ1: Discordサーバーとチャンネルを準備

1. Discordにログイン
2. 投稿先のサーバーを選択（または新規作成）
3. 投稿先のテキストチャンネルを選択（または新規作成）

> 💡 **推奨**: フォーラムチャンネルを作成すると、各録画が個別のスレッドとして整理されます。

#### ステップ2: チャンネル設定を開く

1. 投稿先チャンネルの右側にある**⚙️（歯車アイコン）**をクリック
2. 「**チャンネルの編集**」メニューが開きます

#### ステップ3: Webhookを作成

1. 左サイドバーから「**連携サービス**」をクリック
2. 「**ウェブフックを作成**」をクリック
3. Webhook設定画面が表示されます

#### ステップ4: Webhookをカスタマイズ（任意）

以下の項目を設定できます：

- **名前**: "Zoom講義Bot"（デフォルトで表示される名前）
- **アイコン**: Botのアイコン画像をアップロード
- **チャンネル**: 投稿先チャンネル（変更可能）

#### ステップ5: Webhook URLをコピー

1. 「**ウェブフックURLをコピー**」ボタンをクリック
2. URLが以下の形式でコピーされます：

```plaintext
https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
```

#### ステップ6: 変更を保存

「**変更を保存**」をクリックして完了です。

### 🧪 テスト方法

以下のコマンドでWebhookが正常に動作するかテストできます：

```bash
curl -X POST "<Webhook URL>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "テストメッセージ",
    "username": "Zoom講義Bot"
  }'
```

Discordチャンネルにメッセージが表示されればOKです。

### ⚠️ セキュリティ注意事項

- Webhook URLは**秘密情報**です。公開リポジトリにコミットしないでください
- URLを知っている人は誰でもそのチャンネルに投稿できます
- 漏洩した場合は、Webhookを削除して再作成してください

### ✅ 確認事項

- [ ] Webhook URLを取得した
- [ ] テストメッセージの送信に成功した
- [ ] URLを安全に保管した

### 🎯 GitHub Secretsに設定

```yaml
DISCORD_WEBHOOK_URL: <取得したWebhook URL>
```

---

## 4️⃣ GitHub Personal Access Token の取得方法（オプション）

### 📍 概要

Zoom Webhookから`repository_dispatch`イベントを発火させるために必要です。

### 🔗 公式リンク

- **Personal Access Tokens**: https://github.com/settings/tokens

### 📝 手順

#### ステップ1: GitHub設定にアクセス

1. GitHubにログイン
2. 右上のプロフィールアイコン → 「**Settings**」
3. 左サイドバー最下部「**Developer settings**」
4. 「**Personal access tokens**」→「**Tokens (classic)**」

#### ステップ2: 新しいトークンを生成

1. 「**Generate new token**」→「**Generate new token (classic)**」
2. 以下を設定：

   - **Note**: "Zoom Webhook Dispatcher"
   - **Expiration**: "No expiration"（または適切な期間）
   - **Scopes**: 「**repo**」にチェック

3. 「**Generate token**」をクリック

#### ステップ3: トークンをコピー

```plaintext
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **重要**: このトークンは一度しか表示されません。

### 🎯 使用方法

Zoom Webhook側で以下のリクエストを送信：

```bash
curl -X POST \
  https://api.github.com/repos/<owner>/<repo>/dispatches \
  -H "Authorization: token <GitHub Token>" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
    "event_type": "zoom_recording_completed",
    "client_payload": {
      "meeting_uuid": "abc123",
      "meeting_topic": "講義タイトル"
    }
  }'
```

### ✅ 確認事項

- [ ] Personal Access Tokenを取得した
- [ ] `repo`スコープを付与した

---

## 5️⃣ GitHub Secrets への設定方法

取得したすべての認証情報をGitHub Secretsに安全に保存します。

### 📝 手順

#### ステップ1: リポジトリ設定を開く

1. GitHubリポジトリページにアクセス
2. 「**Settings**」タブをクリック
3. 左サイドバー「**Secrets and variables**」→「**Actions**」

#### ステップ2: Secretを追加

「**New repository secret**」をクリックし、以下を1つずつ追加：

| Name | Value |
|------|-------|
| `ZOOM_API_KEY` | Zoom API Key |
| `ZOOM_API_SECRET` | Zoom API Secret |
| `OPENAI_API_KEY` | OpenAI API Key |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |
| `MIN_RECORDING_DURATION` | `30`（任意: 最小録画時間） |

#### ステップ3: 設定を確認

Secretsページに以下が表示されればOK：

```
✅ ZOOM_API_KEY
✅ ZOOM_API_SECRET
✅ OPENAI_API_KEY
✅ DISCORD_WEBHOOK_URL
✅ MIN_RECORDING_DURATION
```

### 🔒 セキュリティベストプラクティス

- ✅ Secretsは暗号化されて保存されます
- ✅ ログには`***`としてマスクされます
- ✅ プルリクエストからはアクセスできません
- ❌ 公開リポジトリでも使用できますが、注意が必要です

---

## 6️⃣ 動作確認

すべてのAPI設定が完了したら、GitHub Actionsで手動実行してテストします。

### 📝 手順

1. GitHubリポジトリの「**Actions**」タブに移動
2. 「**Zoom to Discord Auto Post**」ワークフローを選択
3. 「**Run workflow**」をクリック
4. Meeting UUIDを入力（テスト用の録画UUID）
5. 「**Run workflow**」で実行

### ✅ 成功の確認

- GitHub Actionsのログに「🎉 Discord投稿完了！」と表示
- Discordチャンネルに投稿が表示される
- ログArtifactがダウンロード可能

### ❌ エラー時の対処

| エラーメッセージ | 原因 | 対処法 |
|----------------|------|--------|
| `❌ 録画情報の取得に失敗` | Zoom API認証エラー | API KeyとSecretを再確認 |
| `❌ GPT-5 API呼び出しエラー` | OpenAI APIキーエラー | APIキーと課金設定を確認 |
| `❌ Discord投稿に失敗` | Webhook URLエラー | Webhook URLを再確認 |

---

## 📚 参考リンク

### 公式ドキュメント

- **Zoom API**: https://marketplace.zoom.us/docs/api-reference/
- **OpenAI API**: https://platform.openai.com/docs/
- **Discord Webhooks**: https://discord.com/developers/docs/resources/webhook
- **GitHub Actions**: https://docs.github.com/en/actions

### トラブルシューティング

- **Zoom API FAQ**: https://marketplace.zoom.us/docs/faq
- **OpenAI Status**: https://status.openai.com/
- **Discord Status**: https://discordstatus.com/

---

## 🎉 完了！

これで全てのAPI設定が完了しました。

次は実際にZoom録画を完了させて、自動投稿が動作するか確認してみましょう！

何か問題が発生した場合は、各APIの公式ドキュメントを参照するか、GitHub Issuesで質問してください。

