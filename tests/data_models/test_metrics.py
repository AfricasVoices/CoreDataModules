import unittest

from core_data_modules.data_models import MessagesMetrics


class TestMessagesMetrics(unittest.TestCase):
    def test___add__(self):
        self.assertEqual(
            MessagesMetrics(40, 30, 20, 10) + MessagesMetrics(-1, 1, 2, 3),
            MessagesMetrics(39, 31, 22, 13)
        )

    def test___sub__(self):
        self.assertEqual(
            MessagesMetrics(40, 30, 20, 10) - MessagesMetrics(-1, 1, 2, 3),
            MessagesMetrics(41, 29, 18, 7)
        )

