# 🎯 Zoom → Discord 自動投稿ワークフロー

Zoomミーティングの録画完了後、GPT-5でタイトル生成、Canvaでサムネイル作成、Discordフォーラムに自動投稿するGitHub Actionsワークフローです。

## 🌟 特徴

- **🤖 GPT-5連携**: 最新のGPT-5 APIで魅力的なタイトルと説明文を自動生成
- **🎨 サムネイル自動生成**: Canva APIまたはPillowでサムネイル画像を生成
- **📤 Discord自動投稿**: フォーラムチャンネルに講義情報を整理して投稿
- **🔄 完全自動化**: Zoom Webhookからの完全自動実行

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
│   ├── canva_thumbnail.py          # Canva/Pillow サムネイル生成
│   ├── discord_poster.py           # Discord 投稿ハンドラー
│   └── requirements.txt            # Python依存関係
├── templates/
│   └── canva_template.json         # Canvaテンプレート設定
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
| `CANVA_API_KEY` | Canva APIキー | ⚠️ |
| `CANVA_TEMPLATE_ID` | 既存Canvaテンプレートの ID | ⚠️ |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | ✅ |

> ⚠️ Canva APIはEnterpriseアカウントが必要です。既存のテンプレートにAI生成テキストを挿入します。未設定の場合はサムネイル生成をスキップします。

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
3. 録画情報取得 → GPT-5でコンテンツ生成
4. Canvaでサムネイル生成 → Discord投稿

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
- **Canva API**: Enterpriseプラン料金

### ログ確認

GitHub Actions実行時のログはArtifactとしてダウンロード可能：

```
logs/
└── zoom_discord_YYYYMMDD_HHMMSS.log
```

## 🎨 サムネイル生成

### Canva APIを使用した既存テンプレート活用

- **Autofill API**: 既存テンプレートにAI生成テキストを自動挿入
- **既存デザイン活用**: ブランド統一されたプロ品質のサムネイル
- **動的テキスト挿入**: GPT-5生成タイトルをテンプレートに動的配置

## 📤 Discord投稿内容

生成される投稿には以下が含まれます：

- **📝 タイトル**: GPT-5生成の魅力的なタイトル
- **📄 説明**: 講義概要（200-300文字）
- **🎥 録画リンク**: Zoom録画視聴URL
- **🖼️ サムネイル**: 自動生成されたサムネイル画像
- **🏷️ タグ**: 関連キーワード
- **⏰ タイムスタンプ**: 投稿日時

## 🛠️ トラブルシューティング

### よくある問題

#### 1. GPT-5 API エラー
```
❌ GPT-5 API呼び出しエラー
```
- OpenAI APIキーが有効か確認
- GPT-5利用権限があるか確認

#### 2. Canva テンプレート関連エラー
```
⚠️ CANVA_TEMPLATE_ID が設定されていません
❌ Autofill API失敗
```
- Canva APIキーとテンプレートIDを確認
- テンプレートがAutofill対応か確認
- Enterpriseアカウントが有効か確認

#### 3. Zoom録画取得失敗
```
❌ 録画情報の取得に失敗しました
```
- Zoom API認証情報を確認
- Meeting UUIDが正しいか確認
- 録画が完了しているか確認

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

### v1.0.0 (2025-09-27)
- 初回リリース
- GPT-5 API連携実装
- Canva API/Pillow サムネイル生成
- Discord Webhook投稿機能
- GitHub Actions ワークフロー

## 📄 ライセンス

MIT License

## 🙋‍♂️ サポート

質問やバグ報告は[Issues](https://github.com/nanameru/zoom-discord-workflows/issues)でお気軽にどうぞ！

---

**🎉 Happy Learning with Automated Workflows! 🎉**