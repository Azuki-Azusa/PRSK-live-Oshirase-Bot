import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from event import Event
from live import Live
from participation import Participation


class StubLive:
    def __init__(self, live_id):
        self.live_id = live_id

    def getID(self):
        return self.live_id


class EventTest(unittest.TestCase):
    def test_matches_event_ending_warning_time(self):
        event = Event({"id": 10, "name": "event", "startAt": 1_700_000_000_000, "aggregateAt": 1_700_003_600_000})
        warning_time = ((1_700_003_600_000 + 1000) // 60000 * 60000) - 60 * 60 * 1000

        self.assertTrue(event.isMatched(warning_time, 1))
        self.assertFalse(event.isMatched(warning_time - 60000, 1))

    def test_getters_return_event_fields(self):
        event = Event({"id": 10, "name": "event", "startAt": 1_700_000_000_000, "aggregateAt": 1_700_003_600_000})

        self.assertEqual(event.getID(), 10)
        self.assertEqual(event.getName(), "event")
        self.assertIn(" ~ ", event.getSchedule())


class LiveTest(unittest.TestCase):
    def test_matches_any_schedule_start_minute(self):
        live = Live({
            "id": 20,
            "name": "live",
            "virtualLiveSchedules": [
                {"startAt": 1_700_000_000_123, "endAt": 1_700_000_600_000},
                {"startAt": 1_700_001_200_999, "endAt": 1_700_001_800_000},
            ],
        })

        self.assertTrue(live.isMatched(1_700_000_000_123 // 60000 * 60000))
        self.assertTrue(live.isMatched(1_700_001_200_999 // 60000 * 60000))
        self.assertFalse(live.isMatched(1_700_002_400_000))

    def test_getters_return_live_fields(self):
        schedules = [{"startAt": 1_700_000_000_000, "endAt": 1_700_000_600_000}]
        live = Live({"id": 20, "name": "live", "virtualLiveSchedules": schedules})

        self.assertEqual(live.getID(), 20)
        self.assertEqual(live.getName(), "live")
        self.assertEqual(live.getScheduleTimestamp(), schedules)
        self.assertIn(" ~ ", live.getSchedule())

    def test_schedule_uses_newline_between_multiple_schedules(self):
        live = Live({
            "id": 20,
            "name": "live",
            "virtualLiveSchedules": [
                {"startAt": 1_700_000_000_000, "endAt": 1_700_000_600_000},
                {"startAt": 1_700_001_200_000, "endAt": 1_700_001_800_000},
            ],
        })

        self.assertEqual(live.getSchedule().count("\n"), 1)


class ParticipationTest(unittest.TestCase):
    def test_tracks_members_who_have_not_participated(self):
        participation = Participation(["100", "200"])
        participation.update([StubLive(1)])

        self.assertEqual(participation.getMentionList(1), [100, 200])

        participation.participate(100, 1)

        self.assertEqual(participation.getMentionList(1), [200])

    def test_update_keeps_existing_log_and_drops_old_lives(self):
        participation = Participation(["100", "200"])
        participation.update([StubLive(1), StubLive(2)])
        participation.participate(100, 1)

        participation.update([StubLive(1), StubLive(3)])

        self.assertEqual(participation.getMentionList(1), [200])
        self.assertEqual(participation.getMentionList(2), [])
        self.assertEqual(participation.getMentionList(3), [100, 200])

    def test_instances_do_not_share_participation_state(self):
        first = Participation(["100"])
        second = Participation(["200"])
        first.update([StubLive(1)])
        second.update([StubLive(1)])

        first.participate(100, 1)

        self.assertEqual(first.getMentionList(1), [])
        self.assertEqual(second.getMentionList(1), [200])


if __name__ == "__main__":
    unittest.main()