"""
GPT-5 API コンテンツジェネレーター
Zoom録画情報から日本語のタイトルと説明を生成
"""

import os
import openai
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class GPT5Generator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        # OpenAI クライアントを初期化（GPT-5対応）
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_content(self, recording_data: Dict, meeting_topic: str = '') -> Optional[Dict]:
        """
        録画データからGPT-5を使用してコンテンツを生成

        Args:
            recording_data: Zoom録画データ
            meeting_topic: ミーティングトピック（任意）

        Returns:
            生成されたコンテンツ（タイトル、説明、タグ）
        """
        try:
            logger.info("GPT-5でコンテンツ生成を開始")

            # プロンプトを構築
            prompt = self._build_prompt(recording_data, meeting_topic)

            # GPT-5 APIを呼び出し
            response = self.client.chat.completions.create(
                model="gpt-5",  # GPT-5の最高性能モデル
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
                # GPT-5の新機能を活用
                verbosity="medium",  # 適切な長さの応答
                reasoning_effort="standard"  # 高品質な推論
            )

            content = response.choices[0].message.content.strip()

            # レスポンスをパース
            parsed_content = self._parse_response(content)

            if parsed_content:
                logger.info(f"GPT-5コンテンツ生成成功: {parsed_content['title']}")
                return parsed_content
            else:
                logger.error("GPT-5レスポンスのパースに失敗")
                return None

        except Exception as e:
            logger.error(f"GPT-5 API呼び出しエラー: {str(e)}")

            # フォールバック：基本的なタイトル生成
            return self._generate_fallback_content(recording_data, meeting_topic)

    def _get_system_prompt(self) -> str:
        """システムプロンプトを取得"""
        return """
あなたは教育コンテンツの専門家です。Zoomの録画情報から、日本語で魅力的な講義タイトルと説明文を生成してください。

出力は以下のJSON形式で返してください：
{
    "title": "魅力的な講義タイトル（50文字以内）",
    "description": "講義の概要説明（200-300文字）",
    "tags": ["キーワード1", "キーワード2", "キーワード3"]
}

要件：
- タイトルは興味を引く表現にする
- 説明は具体的で価値がわかる内容
- タグは関連するキーワード3-5個
- すべて日本語で記述
- Discord投稿に適した形式
"""

    def _build_prompt(self, recording_data: Dict, meeting_topic: str) -> str:
        """プロンプトを構築"""
        prompt_parts = [
            "以下のZoom録画情報から、講義のタイトルと説明を生成してください：",
            "",
            f"ミーティングトピック: {recording_data.get('topic', meeting_topic or 'N/A')}",
            f"開始時刻: {recording_data.get('start_time', 'N/A')}",
            f"録画時間: {recording_data.get('duration', 0)} 分",
            f"録画ファイル数: {recording_data.get('recording_count', 0)}"
        ]

        # トランスクリプトがある場合は追加
        if 'transcript' in recording_data:
            transcript_preview = recording_data['transcript'][:500]  # 最初の500文字
            prompt_parts.extend([
                "",
                "トランスクリプト（抜粋）:",
                transcript_preview + "..."
            ])

        # 録画ファイル情報を追加
        if recording_data.get('recording_files'):
            prompt_parts.extend([
                "",
                "録画ファイル情報:"
            ])
            for file_info in recording_data['recording_files'][:3]:  # 最大3ファイル
                file_type = file_info.get('file_type', 'N/A')
                file_size = file_info.get('file_size', 0)
                size_mb = round(file_size / (1024 * 1024), 1) if file_size else 0
                prompt_parts.append(f"- {file_type} ({size_mb}MB)")

        prompt_parts.extend([
            "",
            "この情報を基に、教育的価値を強調した魅力的なタイトルと説明文を日本語で生成してください。"
        ])

        return "\n".join(prompt_parts)

    def _parse_response(self, content: str) -> Optional[Dict]:
        """GPT-5のレスポンスをパース"""
        try:
            import json

            # JSONブロックを抽出
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)

                # 必要なフィールドをチェック
                if 'title' in parsed and 'description' in parsed:
                    return {
                        'title': parsed['title'][:100],  # 最大100文字
                        'description': parsed['description'][:500],  # 最大500文字
                        'tags': parsed.get('tags', [])[:5]  # 最大5タグ
                    }

            return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {str(e)}")
            return None

    def _generate_fallback_content(self, recording_data: Dict, meeting_topic: str) -> Dict:
        """フォールバック用の基本コンテンツ生成"""
        logger.info("フォールバックコンテンツを生成")

        topic = recording_data.get('topic', meeting_topic or '講義録画')
        duration = recording_data.get('duration', 0)

        # 基本的なタイトル生成
        if '講座' in topic or '講義' in topic:
            title = f"📚 {topic}"
        elif 'セミナー' in topic or 'ワークショップ' in topic:
            title = f"🎯 {topic}"
        elif 'ミーティング' in topic or '会議' in topic:
            title = f"💼 {topic}"
        else:
            title = f"🎥 {topic}"

        # 基本的な説明文生成
        description = f"録画時間: {duration}分\n\n"
        description += f"{topic}の録画です。"

        if duration > 60:
            description += "内容豊富な講義となっております。"

        description += "\n\nぜひご視聴ください！"

        # 基本的なタグ生成
        tags = ["講義", "録画"]
        if 'AI' in topic.upper():
            tags.append("AI")
        if 'プログラミング' in topic:
            tags.append("プログラミング")

        return {
            'title': title[:100],
            'description': description[:500],
            'tags': tags
        }