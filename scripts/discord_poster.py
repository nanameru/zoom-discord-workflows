"""
Discord Webhook 投稿ハンドラー
フォーラムチャンネルへの講義情報投稿
"""

import os
import requests
import logging
from typing import Optional, List, Dict
import json

logger = logging.getLogger(__name__)


class DiscordPoster:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("Discord Webhook URL not found in environment variables")

    def post_to_forum(
        self,
        title: str,
        description: str,
        zoom_url: str,
        thumbnail_url: Optional[str] = None,
        tags: List[str] = None
    ) -> bool:
        """
        Discordフォーラムに投稿

        Args:
            title: 投稿タイトル
            description: 説明文
            zoom_url: Zoom録画URL
            thumbnail_url: サムネイル画像URL
            tags: タグリスト

        Returns:
            投稿成功の可否
        """
        try:
            logger.info(f"Discord投稿開始: {title}")

            # Embedメッセージを構築
            embed = self._build_embed(title, description, zoom_url, thumbnail_url, tags)

            # Discord Webhook形式のペイロードを作成
            payload = {
                "embeds": [embed],
                "username": "Zoom講義Bot",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
            }

            # ファイル添付がある場合
            files = None
            if thumbnail_url and thumbnail_url.startswith('/'):
                # ローカルファイルの場合
                files = self._prepare_file_upload(thumbnail_url)
                if files:
                    # ファイル添付の場合、embedの画像URLを調整
                    embed["image"] = {"url": "attachment://thumbnail.png"}

            # Discord Webhookに送信
            response = self._send_webhook(payload, files)

            if response and response.status_code in [200, 204]:
                logger.info("✅ Discord投稿成功")
                return True
            else:
                logger.error(f"❌ Discord投稿失敗: {response.status_code if response else 'No response'}")
                if response:
                    logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Discord投稿エラー: {str(e)}", exc_info=True)
            return False

    def _build_embed(
        self,
        title: str,
        description: str,
        zoom_url: str,
        thumbnail_url: Optional[str],
        tags: List[str]
    ) -> Dict:
        """Discord Embedメッセージを構築"""

        # カラーコード（青系）
        color = 0x4A90E2

        embed = {
            "title": title[:256],  # Discord title limit
            "description": description[:4096],  # Discord description limit
            "color": color,
            "timestamp": self._get_current_timestamp(),
            "footer": {
                "text": "Zoom講義録画システム",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
            },
            "fields": []
        }

        # Zoom URL フィールド
        if zoom_url:
            embed["fields"].append({
                "name": "🎥 録画視聴",
                "value": f"[こちらから視聴できます]({zoom_url})",
                "inline": False
            })

        # タグフィールド
        if tags:
            tag_text = " ".join([f"`{tag}`" for tag in tags[:10]])  # 最大10タグ
            embed["fields"].append({
                "name": "🏷️ タグ",
                "value": tag_text,
                "inline": False
            })

        # サムネイル設定
        if thumbnail_url:
            if thumbnail_url.startswith('http'):
                # URL形式の場合
                embed["image"] = {"url": thumbnail_url}
            # ローカルファイルの場合は後で処理

        return embed

    def _prepare_file_upload(self, file_path: str) -> Optional[Dict]:
        """ファイルアップロード用のデータを準備"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return {
                        'file': ('thumbnail.png', f.read(), 'image/png')
                    }
        except Exception as e:
            logger.warning(f"ファイルアップロード準備失敗: {str(e)}")

        return None

    def _send_webhook(self, payload: Dict, files: Optional[Dict] = None) -> Optional[requests.Response]:
        """Discord Webhookに送信"""
        try:
            headers = {}

            if files:
                # ファイル添付がある場合
                response = requests.post(
                    self.webhook_url,
                    data={'payload_json': json.dumps(payload)},
                    files=files,
                    timeout=30
                )
            else:
                # 通常のJSON送信
                headers['Content-Type'] = 'application/json'
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook送信エラー: {str(e)}")
            return None

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプをISO形式で取得"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def send_test_message(self) -> bool:
        """テスト用のメッセージを送信"""
        logger.info("テストメッセージを送信")

        embed = {
            "title": "🧪 Zoom講義Bot テスト",
            "description": "Zoom → Discord 自動投稿システムのテストメッセージです。",
            "color": 0x00FF00,
            "timestamp": self._get_current_timestamp(),
            "fields": [
                {
                    "name": "✅ 接続確認",
                    "value": "Webhookが正常に動作しています",
                    "inline": False
                }
            ],
            "footer": {
                "text": "テスト実行中",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
            }
        }

        payload = {
            "embeds": [embed],
            "username": "Zoom講義Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
        }

        response = self._send_webhook(payload)

        if response and response.status_code in [200, 204]:
            logger.info("✅ テストメッセージ送信成功")
            return True
        else:
            logger.error("❌ テストメッセージ送信失敗")
            return False

    def post_error_notification(self, error_message: str, context: Dict = None) -> bool:
        """エラー通知を送信"""
        logger.info("エラー通知を送信")

        embed = {
            "title": "⚠️ Zoom講義Bot エラー",
            "description": f"自動投稿処理中にエラーが発生しました。\n\n```\n{error_message}\n```",
            "color": 0xFF0000,
            "timestamp": self._get_current_timestamp(),
            "footer": {
                "text": "エラー通知",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
            }
        }

        if context:
            fields = []
            for key, value in context.items():
                fields.append({
                    "name": key,
                    "value": str(value),
                    "inline": True
                })
            embed["fields"] = fields

        payload = {
            "embeds": [embed],
            "username": "Zoom講義Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2111/2111728.png"
        }

        response = self._send_webhook(payload)

        return response and response.status_code in [200, 204]