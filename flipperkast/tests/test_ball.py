import unittest
from game.ball import Ball

class TestBall(unittest.TestCase):
    def test_move(self):
        ball = Ball(0, 0)
        ball.velocity_x = 5
        ball.velocity_y = -2
        ball.move()
        self.assertEqual(ball.x, 5)
        self.assertEqual(ball.y, -2)

if __name__ == '__main__':
    unittest.main()
