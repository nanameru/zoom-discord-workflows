"""
Zoom API ハンドラー
録画情報とトランスクリプトの取得
"""

import os
import jwt
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ZoomHandler:
    def __init__(self):
        self.api_key = os.getenv('ZOOM_API_KEY')
        self.api_secret = os.getenv('ZOOM_API_SECRET')
        self.base_url = 'https://api.zoom.us/v2'

        if not self.api_key or not self.api_secret:
            raise ValueError("Zoom API credentials not found in environment variables")

    def _generate_jwt_token(self) -> str:
        """JWTトークンを生成"""
        payload = {
            'iss': self.api_key,
            'exp': int(time.time() + 3600)  # 1時間有効
        }
        return jwt.encode(payload, self.api_secret, algorithm='HS256')

    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """Zoom APIリクエストを実行"""
        try:
            token = self._generate_jwt_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            url = f"{self.base_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, headers=headers, params=params or {})
            else:
                response = requests.request(method, url, headers=headers, json=params or {})

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Zoom API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None

    def get_recording_info(self, meeting_uuid: str) -> Optional[Dict]:
        """録画情報を取得"""
        logger.info(f"録画情報を取得中: {meeting_uuid}")

        # UUIDのダブルエンコーディング対応
        if meeting_uuid.count('%') == 0:
            meeting_uuid = meeting_uuid.replace('/', '%2F').replace('+', '%2B')

        endpoint = f"/meetings/{meeting_uuid}/recordings"
        recording_data = self._make_request(endpoint)

        if not recording_data:
            logger.error("録画データの取得に失敗")
            return None

        # 基本情報を整理
        result = {
            'uuid': recording_data.get('uuid'),
            'id': recording_data.get('id'),
            'topic': recording_data.get('topic', ''),
            'start_time': recording_data.get('start_time'),
            'duration': recording_data.get('duration', 0),
            'total_size': recording_data.get('total_size', 0),
            'recording_count': recording_data.get('recording_count', 0),
            'share_url': recording_data.get('share_url', ''),
            'recording_files': []
        }

        # 録画ファイル情報を整理
        for file_info in recording_data.get('recording_files', []):
            file_data = {
                'id': file_info.get('id'),
                'meeting_id': file_info.get('meeting_id'),
                'recording_start': file_info.get('recording_start'),
                'recording_end': file_info.get('recording_end'),
                'file_type': file_info.get('file_type'),
                'file_extension': file_info.get('file_extension'),
                'file_size': file_info.get('file_size'),
                'play_url': file_info.get('play_url'),
                'download_url': file_info.get('download_url')
            }
            result['recording_files'].append(file_data)

        # トランスクリプトの取得を試行
        transcript = self._get_transcript(meeting_uuid)
        if transcript:
            result['transcript'] = transcript

        logger.info(f"録画情報取得完了: {result['topic']}")
        return result

    def _get_transcript(self, meeting_uuid: str) -> Optional[str]:
        """トランスクリプトを取得（可能な場合）"""
        try:
            endpoint = f"/meetings/{meeting_uuid}/recordings/transcript"
            transcript_data = self._make_request(endpoint)

            if transcript_data and 'transcript' in transcript_data:
                logger.info("トランスクリプト取得成功")
                return transcript_data['transcript']

        except Exception as e:
            logger.warning(f"トランスクリプト取得失敗（スキップ）: {str(e)}")

        return None

    def get_meeting_participants(self, meeting_uuid: str) -> Optional[Dict]:
        """ミーティング参加者情報を取得"""
        endpoint = f"/meetings/{meeting_uuid}/participants"
        participants_data = self._make_request(endpoint)

        if participants_data:
            logger.info(f"参加者数: {participants_data.get('total_records', 0)}")

        return participants_data