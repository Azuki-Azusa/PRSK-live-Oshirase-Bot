import importlib
import importlib.util
import sys
import types
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def is_missing_module(name):
    try:
        return name not in sys.modules and importlib.util.find_spec(name) is None
    except ValueError:
        return False


if is_missing_module("discord"):
    discord = types.ModuleType("discord")
    discord_ext = types.ModuleType("discord.ext")
    tasks = types.ModuleType("discord.ext.tasks")

    class FakeIntents:
        @classmethod
        def all(cls):
            return cls()

        @classmethod
        def default(cls):
            return cls()

    class FakeClient:
        instances = []

        def __init__(self, intents=None):
            self.intents = intents
            self.user = object()
            self.run_calls = []
            FakeClient.instances.append(self)

        def event(self, func):
            return func

        def get_channel(self, _channel_id):
            return None

        def run(self, token):
            self.run_calls.append(token)

    class FakeLoop:
        def __init__(self, func):
            self.func = func
            self.started = False

        def __get__(self, instance, owner):
            return self

        def is_running(self):
            return self.started

        def start(self):
            self.started = True

        async def __call__(self, *args, **kwargs):
            return await self.func(*args, **kwargs)

    def loop(*_args, **_kwargs):
        def decorator(func):
            return FakeLoop(func)
        return decorator

    class FakeFile:
        def __init__(self, fp=None, filename=None):
            self.fp = fp
            self.filename = filename

    discord.Intents = FakeIntents
    discord.Client = FakeClient
    discord.File = FakeFile
    tasks.loop = loop
    discord_ext.tasks = tasks
    sys.modules["discord"] = discord
    sys.modules["discord.ext"] = discord_ext
    sys.modules["discord.ext.tasks"] = tasks

if is_missing_module("aiohttp"):
    aiohttp = types.ModuleType("aiohttp")
    aiohttp.ClientSession = lambda: None
    sys.modules["aiohttp"] = aiohttp

if True:
    environs = types.ModuleType("environs")

    class Env:
        values = {
            "BOT_TOKEN": "test-token",
            "CHANNEL_ID_REMIND": "1",
            "CHANNEL_ID_PRSK": "2",
            "CHANNEL_ID_RANK": "3",
            "DELAY": "10",
            "MEMBERS": "100,200",
            "VIRTUAL_LIVE_API": "https://example.test/virtualLives.json",
            "CURRENT_EVENT_API": "https://example.test/events.json",
            "GAME_API_URL": "https://example.test",
            "GAME_API_PATH": "/api",
            "GAME_API_RANK_PATH1": "/event",
            "GAME_API_RANK_PATH2": "/ranking-border",
            "GAME_API_HEADER": "X-Test-Token",
            "GAME_API_TOKEN": "token",
            "APP_ENV": "production",
            "env": "production",
        }

        def read_env(self):
            return None

        def __call__(self, key):
            return self.values[key]

    environs.Env = Env
    sys.modules["environs"] = environs

if is_missing_module("matplotlib"):
    matplotlib = types.ModuleType("matplotlib")
    pyplot = types.ModuleType("matplotlib.pyplot")

    class FakeTable:
        def set_fontsize(self, size):
            self.size = size

        def scale(self, x, y):
            self.scale_value = (x, y)

    class FakeAxes:
        def axis(self, value):
            self.axis_value = value

        def table(self, cellText, loc, cellLoc):
            self.cell_text = cellText
            return FakeTable()

    def use(_backend):
        return None

    def subplots():
        return object(), FakeAxes()

    def savefig(buf, format, bbox_inches):
        buf.write(b"\x89PNG\r\n\x1a\n")

    def close(_fig):
        return None

    matplotlib.use = use
    pyplot.subplots = subplots
    pyplot.savefig = savefig
    pyplot.close = close
    sys.modules["matplotlib"] = matplotlib
    sys.modules["matplotlib.pyplot"] = pyplot


dcbot = importlib.import_module("dcbot")


class FakeAuthor:
    def __init__(self, author_id=100):
        self.id = author_id


class FakeChannel:
    def __init__(self, channel_id):
        self.id = channel_id
        self.sent = []

    async def send(self, content=None, file=None):
        self.sent.append({"content": content, "file": file})


class FakeMessage:
    def __init__(self, channel_id, content, author_id=100):
        self.channel = FakeChannel(channel_id)
        self.content = content
        self.author = FakeAuthor(author_id)


class DcbotHelpersTest(unittest.TestCase):
    def test_parse_live_id_command(self):
        self.assertEqual(dcbot.parse_live_id_command("123"), 123)
        self.assertIsNone(dcbot.parse_live_id_command("abc123"))
        self.assertIsNone(dcbot.parse_live_id_command("123 abc"))

    def test_parse_character_score_command(self):
        self.assertEqual(dcbot.parse_character_score_command("SCORE_33"), 33)
        self.assertEqual(dcbot.parse_character_score_command("score_33"), 33)
        self.assertIsNone(dcbot.parse_character_score_command("SCORE_MAIN"))
        self.assertIsNone(dcbot.parse_character_score_command("SCORE_x"))

    def test_format_mentions(self):
        self.assertEqual(dcbot.format_mentions([100, 200]), "<@100> <@200>")


class DcbotStateTest(unittest.TestCase):
    def test_state_reports_event_readiness(self):
        state = dcbot.BotState()
        self.assertFalse(state.has_event_ready())

        class ReadyEvent:
            def isMatched(self, now, hour):
                return False

        state.event = ReadyEvent()

        self.assertTrue(state.has_event_ready())

    def test_character_rank_queue_is_created_once(self):
        state = dcbot.BotState()

        first = state.get_character_rank_queue(33)
        second = state.get_character_rank_queue(33)

        self.assertIs(first, second)
        self.assertIn(33, state.character_rankings_save_queue)

    def test_reminder_message_builders(self):
        class StubLive:
            def getID(self):
                return 10

            def getName(self):
                return "live"

        class StubEvent:
            def getID(self):
                return 20

            def getName(self):
                return "event"

        live_message = dcbot.build_live_reminder_message(StubLive(), [100])
        event_message = dcbot.build_event_reminder_message(StubEvent(), 1)

        self.assertIn("<@100>", live_message)
        self.assertIn("live", live_message)
        self.assertIn('ライブの時間だよ！', live_message)
        self.assertIn('終了1時間前！', event_message)

    def test_build_schedule_message_handles_empty_state(self):
        old_state = dcbot.state
        try:
            dcbot.state = dcbot.BotState()

            message = dcbot.build_schedule_message()

            self.assertIn("Live", message)
            self.assertIn(dcbot.DATA_NOT_READY_MESSAGE, message)
        finally:
            dcbot.state = old_state


class DcbotHandlerTest(unittest.IsolatedAsyncioTestCase):
    async def test_show_command_sends_schedule_without_ready_event(self):
        old_state = dcbot.state
        try:
            dcbot.state = dcbot.BotState()
            message = FakeMessage(dcbot.CHANNEL_ID_REMIND, "SHOW")

            await dcbot.handle_remind_channel_message(message)

            self.assertEqual(len(message.channel.sent), 1)
            self.assertIn(dcbot.DATA_NOT_READY_MESSAGE, message.channel.sent[0]["content"])
        finally:
            dcbot.state = old_state

    async def test_score_all_without_data_sends_not_ready_message(self):
        old_state = dcbot.state
        try:
            dcbot.state = dcbot.BotState()
            message = FakeMessage(dcbot.CHANNEL_ID_RANK, "SCORE_ALL")

            await dcbot.handle_rank_channel_message(message)

            self.assertEqual(message.channel.sent[0]["content"], dcbot.DATA_NOT_READY_MESSAGE)
        finally:
            dcbot.state = old_state

    async def test_unknown_character_score_sends_message(self):
        old_state = dcbot.state
        try:
            dcbot.state = dcbot.BotState()
            message = FakeMessage(dcbot.CHANNEL_ID_RANK, "SCORE_33")

            await dcbot.handle_rank_channel_message(message)

            self.assertEqual(message.channel.sent[0]["content"], dcbot.UNKNOWN_CHARACTER_MESSAGE)
        finally:
            dcbot.state = old_state


class DcbotStartupTest(unittest.TestCase):
    def test_import_does_not_run_client(self):
        self.assertEqual(dcbot.client.run_calls, [])

    def test_main_runs_client_with_token(self):
        dcbot.client.run_calls.clear()

        dcbot.main()

        self.assertEqual(dcbot.client.run_calls, ["test-token"])


if __name__ == "__main__":
    unittest.main()
