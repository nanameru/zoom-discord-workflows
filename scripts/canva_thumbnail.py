"""
Canva API サムネイルジェネレーター
講義タイトルからサムネイル画像を生成
"""

import os
import requests
import logging
from typing import Optional, Dict
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tempfile

logger = logging.getLogger(__name__)


class CanvaThumbnailGenerator:
    def __init__(self):
        self.api_key = os.getenv('CANVA_API_KEY')
        self.base_url = 'https://api.canva.com/rest/v1'

    def create_thumbnail(self, title: str, subtitle: str = '') -> Optional[str]:
        """
        タイトルからサムネイルを生成

        Args:
            title: メインタイトル
            subtitle: サブタイトル（任意）

        Returns:
            生成されたサムネイルのURL（失敗時はNone）
        """
        logger.info(f"サムネイル生成開始: {title}")

        # Canva API が利用可能な場合
        if self.api_key:
            thumbnail_url = self._create_with_canva(title, subtitle)
            if thumbnail_url:
                return thumbnail_url

        # フォールバック: Pillowで基本的なサムネイルを生成
        logger.info("Canva APIが利用できないため、Pillowでサムネイル生成")
        return self._create_with_pillow(title, subtitle)

    def _create_with_canva(self, title: str, subtitle: str = '') -> Optional[str]:
        """Canva APIを使用してサムネイルを生成"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # デザイン作成リクエスト
            design_data = {
                'design_type': 'Presentation',
                'title': f'講義サムネイル: {title[:30]}',
                'template_id': None,  # カスタムテンプレートIDを指定可能
                'elements': [
                    {
                        'type': 'text',
                        'text': title,
                        'position': {'x': 50, 'y': 100},
                        'font_size': 36,
                        'color': '#FFFFFF',
                        'font_weight': 'bold'
                    }
                ]
            }

            if subtitle:
                design_data['elements'].append({
                    'type': 'text',
                    'text': subtitle,
                    'position': {'x': 50, 'y': 150},
                    'font_size': 24,
                    'color': '#E0E0E0'
                })

            # デザイン作成
            response = requests.post(
                f'{self.base_url}/designs',
                headers=headers,
                json=design_data,
                timeout=30
            )

            if response.status_code == 201:
                design_data = response.json()
                design_id = design_data.get('id')

                if design_id:
                    # 画像エクスポート
                    export_url = self._export_design(design_id, headers)
                    if export_url:
                        logger.info("Canvaサムネイル生成成功")
                        return export_url

        except requests.exceptions.RequestException as e:
            logger.warning(f"Canva API呼び出し失敗: {str(e)}")
        except Exception as e:
            logger.warning(f"Canvaサムネイル生成エラー: {str(e)}")

        return None

    def _export_design(self, design_id: str, headers: Dict) -> Optional[str]:
        """デザインを画像としてエクスポート"""
        try:
            export_data = {
                'format': 'PNG',
                'quality': 'high',
                'width': 1280,
                'height': 720
            }

            response = requests.post(
                f'{self.base_url}/designs/{design_id}/export',
                headers=headers,
                json=export_data,
                timeout=60
            )

            if response.status_code == 200:
                export_result = response.json()
                return export_result.get('export_url')

        except Exception as e:
            logger.error(f"デザインエクスポートエラー: {str(e)}")

        return None

    def _create_with_pillow(self, title: str, subtitle: str = '') -> Optional[str]:
        """Pillowを使用してローカルでサムネイル生成"""
        try:
            # 画像サイズ（YouTube サムネイル推奨サイズ）
            width, height = 1280, 720

            # 背景色を作成（グラデーション風）
            image = Image.new('RGB', (width, height), '#1a1a1a')
            draw = ImageDraw.Draw(image)

            # グラデーション背景を作成
            for y in range(height):
                gradient_color = int(26 + (y / height) * 40)  # 26から66まで
                color = f'#{gradient_color:02x}{gradient_color:02x}{gradient_color:02x}'
                draw.line([(0, y), (width, y)], fill=color)

            # アクセントカラーの四角形を追加
            accent_color = '#4A90E2'
            draw.rectangle([0, 0, 10, height], fill=accent_color)
            draw.rectangle([0, 0, width, 10], fill=accent_color)

            # フォント設定（システムフォントを使用）
            try:
                # macOSの場合
                title_font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', 48)
                subtitle_font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 28)
            except:
                try:
                    # Windowsの場合
                    title_font = ImageFont.truetype('meiryo.ttc', 48)
                    subtitle_font = ImageFont.truetype('meiryo.ttc', 28)
                except:
                    # フォールバック
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()

            # タイトルテキストを描画
            title_lines = self._wrap_text(title, title_font, width - 100, draw)
            title_y = height // 2 - (len(title_lines) * 60) // 2

            for i, line in enumerate(title_lines):
                text_bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (width - text_width) // 2

                # 影を描画
                draw.text((x + 2, title_y + i * 60 + 2), line, font=title_font, fill='#000000')
                # メインテキストを描画
                draw.text((x, title_y + i * 60), line, font=title_font, fill='#FFFFFF')

            # サブタイトルを描画
            if subtitle:
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_x = (width - subtitle_width) // 2
                subtitle_y = title_y + len(title_lines) * 60 + 20

                # 影を描画
                draw.text((subtitle_x + 1, subtitle_y + 1), subtitle, font=subtitle_font, fill='#000000')
                # メインテキストを描画
                draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill='#E0E0E0')

            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image.save(tmp_file.name, 'PNG', quality=95)
                tmp_file_path = tmp_file.name

            logger.info(f"Pillowサムネイル生成成功: {tmp_file_path}")
            return tmp_file_path

        except Exception as e:
            logger.error(f"Pillowサムネイル生成エラー: {str(e)}")
            return None

    def _wrap_text(self, text: str, font, max_width: int, draw) -> list:
        """テキストを指定幅で折り返し"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines[:3]  # 最大3行まで