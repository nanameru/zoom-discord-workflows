"""
Zoom API ハンドラー
録画情報とトランスクリプトの取得
Server-to-Server OAuth対応
"""

import os
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ZoomHandler:
    def __init__(self):
        # Server-to-Server OAuth認証情報
        self.account_id = os.getenv('ZOOM_ACCOUNT_ID')
        self.client_id = os.getenv('ZOOM_CLIENT_ID')
        self.client_secret = os.getenv('ZOOM_CLIENT_SECRET')
        self.base_url = 'https://api.zoom.us/v2'
        
        if not all([self.account_id, self.client_id, self.client_secret]):
            raise ValueError("Zoom API credentials not found in environment variables. Required: ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET")
        
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self) -> str:
        """Server-to-Server OAuthアクセストークンを取得"""
        # トークンがまだ有効な場合は再利用
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # 新しいトークンを取得
        token_url = f'https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}'
        
        response = requests.post(
            token_url,
            auth=(self.client_id, self.client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            # トークンの有効期限を設定（少し余裕を持たせて5分前に更新）
            self.token_expires_at = time.time() + data.get('expires_in', 3600) - 300
            logger.info("✅ Zoom access token取得成功")
            return self.access_token
        else:
            logger.error(f"❌ Zoom access token取得失敗: {response.status_code} {response.text}")
            raise Exception(f"Failed to get Zoom access token: {response.status_code}")

    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """Zoom APIリクエストを実行"""
        try:
            token = self._get_access_token()
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