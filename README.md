# 🎯 Zoom → Discord 自動投稿ワークフロー

Zoomミーティングの録画完了後、GPT-5でタイトル生成、Discordフォーラムに自動投稿するGitHub Actionsワークフローです。

## 🌟 特徴

- **🤖 GPT-5連携**: 最新のGPT-5 APIで魅力的なタイトルと説明文を自動生成
- **📤 Discord自動投稿**: フォーラムチャンネルに講義情報を整理して投稿
- **🔄 完全自動化**: Zoom Webhookからの完全自動実行
- **⏱️ 時間フィルタリング**: 設定した最小録画時間（デフォルト30分）以上のみ処理

## 📁 プロジェクト構造

```
zoom-discord-workflows/
├── .github/
│   └── workflows/
│       └── zoom-to-discord.yaml    # GitHub Actions ワークフロー
├── scripts/
│   ├── main.py                     # メイン処理スクリプト
│   ├── zoom_handler.py             # Zoom API ハンドラー
│   ├── gpt5_generator.py           # GPT-5 コンテンツ生成
│   ├── discord_poster.py           # Discord 投稿ハンドラー
│   └── requirements.txt            # Python依存関係
├── logs/                           # ログファイル
├── .env.example                    # 環境変数テンプレート
└── README.md
```

## 🚀 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/nanameru/zoom-discord-workflows.git
cd zoom-discord-workflows
```

### 2. GitHub Secrets設定

GitHub リポジトリの Settings → Secrets and variables → Actions で以下のシークレットを設定：

| Secret名 | 説明 | 必須 |
|---------|------|------|
| `ZOOM_API_KEY` | Zoom APIキー | ✅ |
| `ZOOM_API_SECRET` | Zoom APIシークレット | ✅ |
| `OPENAI_API_KEY` | OpenAI APIキー（GPT-5対応） | ✅ |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | ✅ |
| `MIN_RECORDING_DURATION` | 最小録画時間（分）デフォルト: 30 | ⚠️ |

> ℹ️ Canva API連携は後日実装予定です。現在はサムネイル生成をスキップして動作します。

### 3. Zoom Webhook設定

1. [Zoom Marketplace](https://marketplace.zoom.us/)でWebhook-only app を作成
2. Webhook設定で `recording.completed` イベントを購読
3. WebhookエンドポイントURLを設定（GitHub repository dispatch経由）

### 4. Discord Webhook設定

1. Discordサーバーの管理画面でWebhookを作成
2. フォーラムチャンネルを対象に設定
3. Webhook URLをGitHub Secretsに設定

## 📋 使用方法

### 自動実行

Zoomミーティングの録画完了時に自動実行されます：

1. Zoom録画完了 → Webhook発火
2. GitHub Actions ワークフロー実行
3. 録画情報取得 → **録画時間チェック（30分以上のみ継続）**
4. GPT-5でコンテンツ生成 → Discord投稿

> 📝 **時間フィルタリング**: 録画時間が設定した最小時間未満の場合、処理をスキップして正常終了します。

### 手動実行

GitHub Actions画面から手動実行も可能：

1. リポジトリの Actions タブに移動
2. "Zoom to Discord Auto Post" ワークフローを選択
3. "Run workflow" → Meeting UUID入力 → 実行

## 🔧 設定詳細

### GPT-5 API設定

```python
# GPT-5の新機能を活用
model="gpt-5"                    # 最高性能モデル
verbosity="medium"               # 適切な長さの応答
reasoning_effort="standard"      # 高品質な推論
```

### コスト目安

- **GPT-5**: $1.25/1M入力 + $10/1M出力
- **GPT-5-mini**: 25%のコスト（代替案）

### ログ確認

GitHub Actions実行時のログはArtifactとしてダウンロード可能：

```
logs/
└── zoom_discord_YYYYMMDD_HHMMSS.log
```

## 📤 Discord投稿内容

生成される投稿には以下が含まれます：

- **📝 タイトル**: GPT-5生成の魅力的なタイトル
- **📄 説明**: 講義概要（200-300文字）
- **🎥 録画リンク**: Zoom録画視聴URL
- **🏷️ タグ**: 関連キーワード（3-5個）
- **⏰ タイムスタンプ**: 投稿日時

## 🛠️ トラブルシューティング

### よくある問題

#### 1. GPT-5 API エラー
```
❌ GPT-5 API呼び出しエラー
```
- OpenAI APIキーが有効か確認
- GPT-5利用権限があるか確認

#### 2. Zoom録画取得失敗
```
❌ 録画情報の取得に失敗しました
```
- Zoom API認証情報を確認
- Meeting UUIDが正しいか確認
- 録画が完了しているか確認

#### 3. 録画時間によるスキップ
```
⏳ 録画時間が30分未満のため、処理をスキップします
```
- これは正常な動作です（エラーではありません）
- `MIN_RECORDING_DURATION` 環境変数で閾値を調整可能
- 短時間の録画を投稿したい場合は閾値を下げてください

#### 4. Discord投稿失敗
```
❌ Discord投稿に失敗しました
```
- Webhook URLが有効か確認
- フォーラムチャンネルの権限を確認
- メッセージサイズ制限（2000文字）を確認

### デバッグ方法

1. **ローカルテスト**:
```bash
python scripts/main.py
```

2. **環境変数確認**:
```bash
# .envファイル作成
cp .env.example .env
# 必要な値を設定後
source .env
```

3. **個別テスト**:
```python
# Discord接続テスト
from scripts.discord_poster import DiscordPoster
poster = DiscordPoster()
poster.send_test_message()
```

## 🔄 更新履歴

### v1.1.0 (2025-10-01)
- サムネイル生成機能を削除（シンプル化）
- 録画時間フィルタリング機能を追加

### v1.0.0 (2025-09-27)
- 初回リリース
- GPT-5 API連携実装
- Discord Webhook投稿機能
- GitHub Actions ワークフロー

## 📄 ライセンス

MIT License

## 🙋‍♂️ サポート

質問やバグ報告は[Issues](https://github.com/nanameru/zoom-discord-workflows/issues)でお気軽にどうぞ！

---

**🎉 Happy Learning with Automated Workflows! 🎉**