#!/usr/bin/env python3
"""
Zoom Recording to Discord Auto-Poster
Zoomの録画完了後、GPT-5でタイトル生成、Canvaでサムネイル作成、Discordに投稿
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# ログ設定
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"zoom_discord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from zoom_handler import ZoomHandler
from gpt5_generator import GPT5Generator
# from canva_thumbnail import CanvaThumbnailGenerator  # 後日実装
from discord_poster import DiscordPoster


def main():
    """メイン処理"""
    try:
        logger.info("🚀 Zoom to Discord 自動投稿プロセスを開始します")

        # 環境変数の取得
        meeting_uuid = os.getenv('MEETING_UUID')
        meeting_topic = os.getenv('MEETING_TOPIC', '')

        if not meeting_uuid:
            logger.error("❌ MEETING_UUID環境変数が設定されていません")
            sys.exit(1)

        logger.info(f"📋 処理対象ミーティング: {meeting_uuid}")
        if meeting_topic:
            logger.info(f"📝 ミーティングトピック: {meeting_topic}")

        # 1. Zoom録画情報を取得
        logger.info("📹 Zoom録画情報を取得中...")
        zoom_handler = ZoomHandler()
        recording_data = zoom_handler.get_recording_info(meeting_uuid)

        if not recording_data:
            logger.error("❌ 録画情報の取得に失敗しました")
            sys.exit(1)

        logger.info(f"✅ 録画情報取得成功: {recording_data.get('topic', 'N/A')}")

        # 1.5. 録画時間チェック（設定された最小時間以上の場合のみ処理を継続）
        duration_minutes = recording_data.get('duration', 0)
        min_duration_threshold = int(os.getenv('MIN_RECORDING_DURATION', '30'))  # 最小録画時間（分）

        logger.info(f"📊 録画時間: {duration_minutes}分")

        if duration_minutes < min_duration_threshold:
            logger.info(f"⏳ 録画時間が{min_duration_threshold}分未満のため、処理をスキップします")
            logger.info(f"   現在の録画時間: {duration_minutes}分 < 閾値: {min_duration_threshold}分")
            logger.info("✨ 処理を正常終了します（投稿なし）")
            return

        logger.info(f"✅ 録画時間が{min_duration_threshold}分以上のため、処理を継続します")

        # 2. GPT-5でタイトルと説明を生成
        logger.info("🤖 GPT-5でコンテンツ生成中...")
        gpt5_generator = GPT5Generator()
        generated_content = gpt5_generator.generate_content(recording_data, meeting_topic)

        if not generated_content:
            logger.error("❌ GPT-5によるコンテンツ生成に失敗しました")
            sys.exit(1)

        logger.info(f"✅ コンテンツ生成成功: {generated_content['title']}")

        # 3. サムネイル生成（現在は無効化）
        logger.info("🎨 サムネイル生成をスキップ（Canva実装は後日対応）")
        thumbnail_url = None

        # 4. Discordに投稿
        logger.info("📤 Discordに投稿中...")
        discord_poster = DiscordPoster()
        success = discord_poster.post_to_forum(
            title=generated_content['title'],
            description=generated_content['description'],
            zoom_url=recording_data.get('share_url', ''),
            thumbnail_url=thumbnail_url,
            tags=generated_content.get('tags', [])
        )

        if success:
            logger.info("🎉 Discord投稿完了！")
        else:
            logger.error("❌ Discord投稿に失敗しました")
            sys.exit(1)

        logger.info("✨ 全ての処理が正常に完了しました")

    except Exception as e:
        logger.error(f"💥 予期しないエラーが発生しました: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()