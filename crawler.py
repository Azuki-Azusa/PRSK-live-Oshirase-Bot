import aiohttp
import asyncio
import json
import time
from environs import Env

# Load .env 文件
env = Env()
env.read_env()

VIRTUAL_LIVE_API = env("VIRTUAL_LIVE_API")
CURRENT_EVENT_API = env("CURRENT_EVENT_API")

GAME_API_URL = env("GAME_API_URL")
GAME_API_PATH = env("GAME_API_PATH")
GAME_API_RANK_PATH1 = env("GAME_API_RANK_PATH1")
GAME_API_RANK_PATH2 = env("GAME_API_RANK_PATH2")
GAME_API_HEADER = env("GAME_API_HEADER")
GAME_API_TOKEN = env("GAME_API_TOKEN")


async def fetch_json(session, url, headers=None):
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


async def getLatestLive():
    async with aiohttp.ClientSession() as session:
        virtual_lives = await fetch_json(session, VIRTUAL_LIVE_API)
        if not virtual_lives:
            return []
        current_time = time.time() * 1000
        current_lives = [
            live for live in virtual_lives
            if live['startAt'] < current_time and live['endAt'] > current_time and live['virtualLiveType'] != 'beginner'
        ]
        return current_lives


async def getCurrentEvent():
    async with aiohttp.ClientSession() as session:
        events = await fetch_json(session, CURRENT_EVENT_API)
        if not events:
            return None
        return events[-1]


async def getCurrentRank():
    async with aiohttp.ClientSession() as session:
        current_event = await getCurrentEvent()
        if not current_event:
            return {}, {}

        event_id = str(current_event["id"])
        url = GAME_API_URL + GAME_API_PATH + GAME_API_RANK_PATH1 + "/" + event_id + GAME_API_RANK_PATH2
        headers = {
            GAME_API_HEADER: GAME_API_TOKEN
        }

        ranking_border = await fetch_json(session, url, headers=headers)
        if not ranking_border:
            return {}, {}

        border_rankings = ranking_border.get("borderRankings", [])
        user_world_bloom_chapter_ranking_borders = ranking_border.get("userWorldBloomChapterRankingBorders", [])

        border_rankings_result = {
            user["rank"]: user["score"] for user in border_rankings
        }

        character_rankings_result = {}
        for character in user_world_bloom_chapter_ranking_borders:
            character_id = character["gameCharacterId"]
            character_rank = {
                user["rank"]: user["score"] for user in character.get("borderRankings", [])
            }
            character_rankings_result[character_id] = character_rank

        return border_rankings_result, character_rankings_result
