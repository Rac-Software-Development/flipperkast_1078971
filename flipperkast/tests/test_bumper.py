import unittest
from game.bumper import Bumper
from game.ball import Ball

class TestBumper(unittest.TestCase):
    def test_collision_detected(self):
        ball = Ball(100, 100)
        bumper = Bumper(100, 100)
        self.assertTrue(bumper.check_collision(ball))

    def test_collision_not_detected(self):
        ball = Ball(0, 0)
        bumper = Bumper(100, 100)
        self.assertFalse(bumper.check_collision(ball))

if __name__ == '__main__':
    unittest.main()
