import importlib.util
import sys
import types
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

CONFIG_VALUES = {
    "BOT_TOKEN": "test-token",
    "CHANNEL_ID_REMIND": "1",
    "CHANNEL_ID_PRSK": "2",
    "CHANNEL_ID_RANK": "3",
    "APP_ENV": "development",
    "env": "production",
    "MEMBERS": "100, 200,,",
    "VIRTUAL_LIVE_API": "https://example.test/virtualLives.json",
    "CURRENT_EVENT_API": "https://example.test/events.json",
    "GAME_API_URL": "https://example.test",
    "GAME_API_PATH": "/api",
    "GAME_API_RANK_PATH1": "/event",
    "GAME_API_RANK_PATH2": "/ranking-border",
    "GAME_API_HEADER": "X-Test-Token",
    "GAME_API_TOKEN": "game-token",
    "DELAY": "10",
}

if importlib.util.find_spec("environs") is None:
    environs = types.ModuleType("environs")

    class Env:
        values = CONFIG_VALUES

        def read_env(self):
            return None

        def __call__(self, key):
            return self.values[key]

    environs.Env = Env
    sys.modules["environs"] = environs

from config import AppConfig


class FakeEnv:
    values = CONFIG_VALUES

    def __call__(self, key):
        return self.values[key]


class AppConfigTest(unittest.TestCase):
    def test_from_env_converts_types_and_splits_members(self):
        config = AppConfig.from_env(FakeEnv())

        self.assertEqual(config.bot_token, "test-token")
        self.assertEqual(config.channel_id_remind, 1)
        self.assertEqual(config.channel_id_prsk, 2)
        self.assertEqual(config.channel_id_rank, 3)
        self.assertEqual(config.app_env, "development")
        self.assertTrue(config.is_development)
        self.assertEqual(config.rank_url(999), "https://example.test/api/event/999/ranking-border")
        self.assertEqual(config.rank_headers(), {"X-Test-Token": "game-token"})
        self.assertEqual(config.members, ["100", "200"])
        self.assertEqual(config.delay, 10)
        self.assertEqual(config.game_api_header, "X-Test-Token")


if __name__ == "__main__":
    unittest.main()