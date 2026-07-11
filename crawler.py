"""获取数据。"""

import json
import time
from dataclasses import dataclass

import aiohttp

from config import AppConfig, load_config

CONFIG = load_config()


@dataclass
class CrawlerClient:
    """API 客户端。"""

    config: AppConfig

    async def fetch_json(self, session, url, headers=None):
        """获取 JSON 数据。"""
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    print(f"[ERROR] HTTP {response.status} from {url}")
                    return None
                text = await response.text()
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON decode error from {url}: {e}")
                    print(f"[DEBUG] Response snippet: {text[:200]}")
                    return None
        except Exception as e:
            print(f"[ERROR] Exception fetching {url}: {e}")
            return None

    async def get_latest_live(self):
        """获取当前 Live。"""
        async with aiohttp.ClientSession() as session:
            virtual_lives = await self.fetch_json(session, self.config.virtual_live_api)
            if not virtual_lives:
                return []
            current_time = time.time() * 1000
            return [
                live for live in virtual_lives
                if live['startAt'] < current_time and live['endAt'] > current_time and live['virtualLiveType'] != 'beginner'
            ]

    async def get_current_event(self):
        """获取当前活动。"""
        async with aiohttp.ClientSession() as session:
            events = await self.fetch_json(session, self.config.current_event_api)
            if not events:
                return None
            return events[-1]

    async def get_current_rank(self):
        """获取当前排名数据。"""
        async with aiohttp.ClientSession() as session:
            current_event = await self.get_current_event()
            if not current_event:
                return {}, {}

            ranking_border = await self.fetch_json(
                session,
                self.config.rank_url(current_event["id"]),
                headers=self.config.rank_headers(),
            )
            if not ranking_border:
                return {}, {}

            border_rankings_result = {
                user["rank"]: user["score"]
                for user in ranking_border.get("borderRankings", [])
            }

            character_rankings_result = {}
            for character in ranking_border.get("userWorldBloomChapterRankingBorders", []):
                character_id = character["gameCharacterId"]
                character_rank = {
                    user["rank"]: user["score"]
                    for user in character.get("borderRankings", [])
                }
                character_rankings_result[character_id] = character_rank

            return border_rankings_result, character_rankings_result

    async def has_current_live(self):
        """判断当前是否有 Live。"""
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_json(session, self.config.current_event_api)
            if not data or not isinstance(data, list):
                return False

            now_ms = int(time.time() * 1000)
            for live in data:
                start_at = live["startAt"]
                aggregate_at = live["aggregateAt"]

                if start_at is None or aggregate_at is None:
                    continue

                if start_at <= now_ms <= aggregate_at:
                    return True

            return False


DEFAULT_CLIENT = CrawlerClient(CONFIG)


# 兼容旧的 dcbot.py 调用。新代码优先直接使用 CrawlerClient 的 snake_case 方法。
async def fetch_json(session, url, headers=None):
    """获取 JSON 数据。"""
    return await DEFAULT_CLIENT.fetch_json(session, url, headers=headers)


async def getLatestLive():
    return await DEFAULT_CLIENT.get_latest_live()


async def getCurrentEvent():
    return await DEFAULT_CLIENT.get_current_event()


async def getCurrentRank():
    return await DEFAULT_CLIENT.get_current_rank()


async def hasCurrentLive():
    return await DEFAULT_CLIENT.has_current_live()
