"""
Canva API サムネイルジェネレーター
既存のCanvaテンプレートにAI生成テキストを挿入してサムネイル画像を生成
"""

import os
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class CanvaThumbnailGenerator:
    def __init__(self):
        self.api_key = os.getenv('CANVA_API_KEY')
        self.template_id = os.getenv('CANVA_TEMPLATE_ID')  # 既存テンプレートID
        self.base_url = 'https://api.canva.com/rest/v1'

    def create_thumbnail(self, title: str, subtitle: str = '') -> Optional[str]:
        """
        既存テンプレートにAI生成テキストを挿入してサムネイルを生成

        Args:
            title: メインタイトル
            subtitle: サブタイトル（任意）

        Returns:
            生成されたサムネイルのURL（失敗時はNone）
        """
        logger.info(f"テンプレートベースサムネイル生成開始: {title}")

        # Canva API が利用可能かつテンプレートIDが設定されている場合
        if self.api_key and self.template_id:
            thumbnail_url = self._create_from_template(title, subtitle)
            if thumbnail_url:
                return thumbnail_url

        # APIキーまたはテンプレートIDが未設定の場合
        if not self.api_key:
            logger.warning("CANVA_API_KEY が設定されていません")
        if not self.template_id:
            logger.warning("CANVA_TEMPLATE_ID が設定されていません")

        logger.warning("Canva APIを使用できないため、サムネイル生成をスキップします")
        return None

    def _create_from_template(self, title: str, subtitle: str = '') -> Optional[str]:
        """既存テンプレートからAI生成テキストを挿入してサムネイル生成"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # テンプレートからデザイン作成
            logger.info(f"テンプレートID {self.template_id} を使用してデザイン作成")

            # Autofill APIを使用してテンプレートにテキストを挿入
            autofill_data = {
                'brand_template_id': self.template_id,
                'data': {
                    'title': title[:60],  # タイトル文字数制限
                    'subtitle': subtitle[:40] if subtitle else '',  # サブタイトル文字数制限
                    'lecture_title': title,  # メインタイトル用
                    'lecture_subtitle': subtitle if subtitle else '講義録画'  # サブタイトル用
                }
            }

            # Autofill APIエンドポイント呼び出し
            response = requests.post(
                f'{self.base_url}/autofills',
                headers=headers,
                json=autofill_data,
                timeout=30
            )

            if response.status_code == 200:
                autofill_result = response.json()
                design_id = autofill_result.get('design', {}).get('id')

                if design_id:
                    logger.info(f"Autofill成功、デザインID: {design_id}")
                    # デザインをエクスポート
                    export_url = self._export_design(design_id, headers)
                    if export_url:
                        logger.info("テンプレートベースサムネイル生成成功")
                        return export_url
                    else:
                        raise Exception("デザインエクスポートに失敗しました")
                else:
                    raise Exception(f"AutofillレスポンスにデザインIDが含まれていません: {autofill_result}")
            else:
                raise Exception(f"Autofill API失敗: {response.status_code}, レスポンス: {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Canva Autofill API呼び出し失敗: {str(e)}")
        except Exception as e:
            logger.error(f"テンプレートベースサムネイル生成エラー: {str(e)}")
            raise e

    def _export_design(self, design_id: str, headers: Dict) -> str:
        """デザインを画像としてエクスポート"""
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
            export_url = export_result.get('export_url')
            if export_url:
                return export_url
            else:
                raise Exception(f"エクスポートレスポンスにURLが含まれていません: {export_result}")
        else:
            raise Exception(f"デザインエクスポート失敗: {response.status_code}, レスポンス: {response.text}")