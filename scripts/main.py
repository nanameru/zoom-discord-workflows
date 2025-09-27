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
from canva_thumbnail import CanvaThumbnailGenerator
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

        # 2. GPT-5でタイトルと説明を生成
        logger.info("🤖 GPT-5でコンテンツ生成中...")
        gpt5_generator = GPT5Generator()
        generated_content = gpt5_generator.generate_content(recording_data, meeting_topic)

        if not generated_content:
            logger.error("❌ GPT-5によるコンテンツ生成に失敗しました")
            sys.exit(1)

        logger.info(f"✅ コンテンツ生成成功: {generated_content['title']}")

        # 3. Canvaでサムネイル生成
        logger.info("🎨 Canvaでサムネイル生成中...")
        canva_generator = CanvaThumbnailGenerator()

        try:
            thumbnail_url = canva_generator.create_thumbnail(generated_content['title'])
            if thumbnail_url:
                logger.info("✅ サムネイル生成成功")
            else:
                logger.error("❌ Canva API設定が不完全です（API KEY または TEMPLATE_ID が未設定）")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ サムネイル生成に失敗しました: {str(e)}")
            sys.exit(1)

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