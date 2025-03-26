import unittest
from unittest.mock import MagicMock
from game.score_panel import ScorePanel

class TestScorePanel(unittest.TestCase):
    def setUp(self):
        self.panel = ScorePanel()
        self.panel.mqtt = MagicMock()

    def test_initial_score(self):
        self.assertEqual(self.panel.scores["Player"], 0)
        self.assertEqual(self.panel.highscore, 0)

    def test_on_message_updates_score(self):
        class MockMsg:
            payload = b'100'

        self.panel.on_message(None, None, MockMsg())
        self.assertEqual(self.panel.scores["Player"], 100)
        self.assertEqual(self.panel.highscore, 100)

        MockMsg.payload = b'50'
        self.panel.on_message(None, None, MockMsg())
        self.assertEqual(self.panel.scores["Player"], 150)
        self.assertEqual(self.panel.highscore, 150)

if __name__ == '__main__':
    unittest.main()
