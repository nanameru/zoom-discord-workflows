# 🌐 Cloudflare Worker: Zoom → GitHub Actions Bridge

このCloudflare WorkerはZoom WebhookからGitHub Actionsへの橋渡しを行います。

## 📋 概要

```
Zoom録画完了
    ↓
Zoom Webhook
    ↓
Cloudflare Worker ← このWorker
    ↓
GitHub API (repository_dispatch)
    ↓
GitHub Actions起動
```

## 🚀 セットアップ手順

### 前提条件

- Cloudflareアカウント（無料）
- Node.js 18以上
- GitHub Personal Access Token

### ステップ1: Cloudflare CLIのインストール

```bash
npm install -g wrangler
```

### ステップ2: Cloudflareにログイン

```bash
wrangler login
```

ブラウザが開き、Cloudflareアカウントでログインします。

### ステップ3: プロジェクトの準備

```bash
cd cloudflare-worker
```

### ステップ4: 環境変数の設定

#### GitHubリポジトリ情報を編集

`wrangler.toml`を開いて、以下を自分の情報に変更：

```toml
[vars]
GITHUB_OWNER = "あなたのGitHubユーザー名"
GITHUB_REPO = "あなたのリポジトリ名"
```

#### GitHub Personal Access Tokenを設定

```bash
wrangler secret put GITHUB_PAT
```

プロンプトが表示されたら、GitHub Personal Access Tokenを入力します。

> 💡 GitHub PATの取得方法は `../API_SETUP_GUIDE.md` の「4️⃣ GitHub Personal Access Token」を参照

### ステップ5: デプロイ

```bash
wrangler deploy
```

デプロイが成功すると、以下のようなURLが表示されます：

```
✨ Successfully published your script to
 https://zoom-github-bridge.your-subdomain.workers.dev
```

このURLをメモしてください。これがZoomに設定するWebhook URLです。

## 🔧 設定

### Zoom Webhook設定

1. Zoom App Marketplace → あなたのアプリ → **Features** タブ
2. **Event Subscriptions** を有効化
3. **Event notification endpoint URL** に以下を設定：
   ```
   https://zoom-github-bridge.your-subdomain.workers.dev
   ```
4. **Add Events** で以下を選択：
   - **Recording** → **All Recordings have completed**
5. **Save**

### GitHub Actionsワークフロー確認

`.github/workflows/zoom-to-discord.yaml` で以下が設定されていることを確認：

```yaml
on:
  repository_dispatch:
    types: [zoom_recording_completed]
```

## 🧪 テスト方法

### ローカルテスト

```bash
wrangler dev
```

ローカルサーバーが起動します（通常は `http://localhost:8787`）。

### エンドポイント検証テスト

```bash
curl -X POST https://zoom-github-bridge.your-subdomain.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "event": "endpoint.url_validation",
    "payload": {
      "plainToken": "test_token",
      "encryptedToken": "encrypted_test"
    }
  }'
```

**期待される応答:**
```json
{
  "plainToken": "test_token",
  "encryptedToken": "encrypted_test"
}
```

### 録画完了イベントテスト

```bash
curl -X POST https://zoom-github-bridge.your-subdomain.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "event": "recording.completed",
    "payload": {
      "object": {
        "uuid": "test-uuid-12345",
        "topic": "テスト講義",
        "duration": 45,
        "start_time": "2025-01-10T10:00:00Z",
        "host_email": "test@example.com"
      }
    }
  }'
```

**期待される応答:**
```json
{
  "success": true,
  "message": "GitHub Actions triggered",
  "meeting_uuid": "test-uuid-12345"
}
```

GitHub Actionsが起動していることを確認してください。

## 📊 ログの確認

### Cloudflareダッシュボードでログ確認

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) にログイン
2. **Workers & Pages** → あなたのWorker
3. **Logs** タブでリアルタイムログを確認

### Wrangler CLIでログ確認

```bash
wrangler tail
```

リアルタイムでログがストリーミングされます。

## 🛠️ トラブルシューティング

### ❌ "401 Unauthorized" エラー

**原因**: GitHub Personal Access Tokenが無効

**対処法**:
```bash
wrangler secret put GITHUB_PAT
```
新しいトークンを設定し直す

### ❌ "404 Not Found" エラー

**原因**: `GITHUB_OWNER` または `GITHUB_REPO` が間違っている

**対処法**:
`wrangler.toml` を確認して正しい値に修正し、再デプロイ

### ❌ Zoomからのリクエストが届かない

**原因**: Event Subscriptionsが正しく設定されていない

**対処法**:
1. Zoom App Marketplace → Event Subscriptions確認
2. エンドポイントURLが正しいか確認
3. `recording.completed` イベントが追加されているか確認

### ⚠️ GitHub Actionsが起動しない

**原因**: ワークフローの設定ミス

**対処法**:
`.github/workflows/zoom-to-discord.yaml` を確認：
```yaml
on:
  repository_dispatch:
    types: [zoom_recording_completed]  # ← これが必須
```

## 💰 コスト

Cloudflare Workersの無料プランで十分です：

| プラン | リクエスト数/日 | CPU時間 | コスト |
|--------|----------------|---------|--------|
| **Free** | 100,000 | 10ms/リクエスト | **無料** |
| **Paid** | 無制限 | 30ms/リクエスト | $5/月〜 |

Zoom録画が1日に100回を超えることはまずないので、無料プランで問題ありません。

## 🔒 セキュリティ

### 推奨事項

1. **GitHub PATは定期的にローテーション**
   ```bash
   wrangler secret put GITHUB_PAT
   ```

2. **最小権限の原則**
   - GitHub PATには `repo` スコープのみ付与

3. **ログの監視**
   - 不審なリクエストがないか定期的に確認

### Webhook署名検証（オプション）

より高度なセキュリティが必要な場合、Zoom Webhookの署名検証を実装できます。

詳細: https://marketplace.zoom.us/docs/api-reference/webhook-reference/#verify-webhook-events

## 📚 参考リンク

- **Cloudflare Workers**: https://workers.cloudflare.com/
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler/
- **Zoom Webhooks**: https://marketplace.zoom.us/docs/api-reference/webhook-reference/
- **GitHub API**: https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event

## 🎉 完了！

これで完全自動化が実現しました！

Zoomで録画が完了すると、自動的にDiscordに投稿されます。

