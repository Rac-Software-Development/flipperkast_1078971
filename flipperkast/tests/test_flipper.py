import unittest
from game.flipper import Flipper
from game.ball import Ball

class TestFlipper(unittest.TestCase):
    def test_flipper_activation(self):
        flipper = Flipper('left')
        flipper.activate()
        self.assertTrue(flipper.active)
        self.assertEqual(flipper.angle, 30)

    def test_flipper_hits_ball(self):
        ball = Ball(0, 0)
        ball.velocity_x = 0
        ball.velocity_y = 5

        flipper = Flipper('right')
        flipper.activate()
        flipper.hit_ball(ball)

        self.assertLess(ball.velocity_y, 0)
        self.assertGreater(ball.velocity_x, 0)

if __name__ == '__main__':
    unittest.main()
