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

import matplotlib
if not hasattr(matplotlib, "use"):
    matplotlib.use = lambda _backend: None
matplotlib.use("Agg")

from rankLogQueue import RankLogQueue


class RankLogQueueTest(unittest.TestCase):
    def test_get_returns_items_in_order_and_respects_max_length(self):
        queue = RankLogQueue(max_length=2, delay=10)

        queue.add({1: 100})
        queue.add({1: 200})
        queue.add({1: 300})

        self.assertEqual(queue.get(), [{1: 200}, {1: 300}])

    def test_speed_per_hour_uses_first_and_last_common_ranks(self):
        queue = RankLogQueue(max_length=3, delay=10)
        queue.add({1: 1000, 2: 500, 3: 1})
        queue.add({1: 1200, 2: 600})
        queue.add({1: 1600, 2: 800, 4: 999})

        self.assertEqual(queue.getSpeedPerhour(), {1: 1800.0, 2: 900.0})

    def test_image_is_false_until_speed_can_be_calculated(self):
        queue = RankLogQueue(max_length=3, delay=10)
        queue.add({1: 1000})

        self.assertFalse(queue.getImageOfScore())

    def test_image_is_png_buffer_when_enough_data_exists(self):
        queue = RankLogQueue(max_length=3, delay=10)
        queue.add({1: 1000})
        queue.add({1: 1500})

        image = queue.getImageOfScore()

        self.assertTrue(image)
        self.assertEqual(image.read(8), b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()