import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

def is_missing_module(name):
    try:
        return name not in sys.modules and importlib.util.find_spec(name) is None
    except ValueError:
        return False


if is_missing_module("aiohttp"):
    aiohttp = types.ModuleType("aiohttp")
    aiohttp.ClientSession = lambda: None
    sys.modules["aiohttp"] = aiohttp

if is_missing_module("environs"):
    environs = types.ModuleType("environs")

    class Env:
        values = {
            "BOT_TOKEN": "test-token",
            "CHANNEL_ID_REMIND": "1",
            "CHANNEL_ID_PRSK": "2",
            "CHANNEL_ID_RANK": "3",
            "DELAY": "10",
            "MEMBERS": "100,200",
            "env": "production",
            "VIRTUAL_LIVE_API": "https://example.test/virtualLives.json",
            "CURRENT_EVENT_API": "https://example.test/events.json",
            "GAME_API_URL": "https://example.test",
            "GAME_API_PATH": "/api",
            "GAME_API_RANK_PATH1": "/event",
            "GAME_API_RANK_PATH2": "/ranking-border",
            "GAME_API_HEADER": "X-Test-Token",
            "GAME_API_TOKEN": "token",
        }

        def read_env(self):
            return None

        def __call__(self, key):
            return self.values[key]

    environs.Env = Env
    sys.modules["environs"] = environs

import crawler


class FakeResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def text(self):
        return self._text


class FakeSession:
    def __init__(self, response=None):
        self.response = response or FakeResponse(200, "{}")
        self.requests = []

    def get(self, url, headers=None, timeout=None):
        self.requests.append({"url": url, "headers": headers, "timeout": timeout})
        return self.response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FetchJsonTest(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_json_returns_decoded_json(self):
        session = FakeSession(FakeResponse(200, json.dumps({"ok": True})))

        result = await crawler.fetch_json(session, "https://example.test", headers={"x": "y"})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(session.requests, [{"url": "https://example.test", "headers": {"x": "y"}, "timeout": 10}])

    async def test_fetch_json_returns_none_for_http_error(self):
        session = FakeSession(FakeResponse(500, "server error"))

        with patch("builtins.print"):
            result = await crawler.fetch_json(session, "https://example.test")

        self.assertIsNone(result)

    async def test_fetch_json_returns_none_for_invalid_json(self):
        session = FakeSession(FakeResponse(200, "not-json"))

        with patch("builtins.print"):
            result = await crawler.fetch_json(session, "https://example.test")

        self.assertIsNone(result)


class CrawlerApiTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_latest_live_filters_current_non_beginner_lives(self):
        lives = [
            {"id": 1, "startAt": 900, "endAt": 1100, "virtualLiveType": "normal"},
            {"id": 2, "startAt": 900, "endAt": 1100, "virtualLiveType": "beginner"},
            {"id": 3, "startAt": 1200, "endAt": 1300, "virtualLiveType": "normal"},
        ]

        with patch.object(crawler.aiohttp, "ClientSession", return_value=FakeSession()), \
             patch.object(crawler.DEFAULT_CLIENT, "fetch_json", AsyncMock(return_value=lives)), \
             patch.object(crawler.time, "time", return_value=1):
            result = await crawler.getLatestLive()

        self.assertEqual([live["id"] for live in result], [1])

    async def test_get_current_event_returns_last_event(self):
        events = [{"id": 1}, {"id": 2}]

        with patch.object(crawler.aiohttp, "ClientSession", return_value=FakeSession()), \
             patch.object(crawler.DEFAULT_CLIENT, "fetch_json", AsyncMock(return_value=events)):
            result = await crawler.getCurrentEvent()

        self.assertEqual(result, {"id": 2})

    async def test_get_current_rank_maps_border_and_character_rankings(self):
        ranking_payload = {
            "borderRankings": [
                {"rank": 100, "score": 12345},
                {"rank": 500, "score": 67890},
            ],
            "userWorldBloomChapterRankingBorders": [
                {
                    "gameCharacterId": 33,
                    "borderRankings": [{"rank": 100, "score": 22222}],
                }
            ],
        }

        with patch.object(crawler.aiohttp, "ClientSession", return_value=FakeSession()), \
             patch.object(crawler.DEFAULT_CLIENT, "get_current_event", AsyncMock(return_value={"id": 999})), \
             patch.object(crawler.DEFAULT_CLIENT, "fetch_json", AsyncMock(return_value=ranking_payload)) as fetch_json:
            border, character = await crawler.getCurrentRank()

        self.assertEqual(border, {100: 12345, 500: 67890})
        self.assertEqual(character, {33: {100: 22222}})
        fetch_json.assert_awaited_once()

    async def test_has_current_live_checks_current_time_range(self):
        data = [
            {"startAt": 1000, "aggregateAt": 1999},
            {"startAt": 2000, "aggregateAt": 4000},
        ]

        with patch.object(crawler.aiohttp, "ClientSession", return_value=FakeSession()), \
             patch.object(crawler.DEFAULT_CLIENT, "fetch_json", AsyncMock(return_value=data)), \
             patch.object(crawler.time, "time", return_value=3):
            result = await crawler.hasCurrentLive()

        self.assertTrue(result)

    async def test_has_current_live_returns_false_for_empty_or_non_list_payload(self):
        with patch.object(crawler.aiohttp, "ClientSession", return_value=FakeSession()), \
             patch.object(crawler.DEFAULT_CLIENT, "fetch_json", AsyncMock(return_value={"not": "a-list"})):
            result = await crawler.hasCurrentLive()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()