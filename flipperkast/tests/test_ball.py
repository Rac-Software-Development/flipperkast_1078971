import unittest
import pymunk
import math
from game.ball import Ball

class TestBall(unittest.TestCase):
    def setUp(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.ball = Ball(self.space, position=(100, 100), radius=15)
        
        self.wall = pymunk.Segment(self.space.static_body, (0, 200), (200, 200), 5)
        self.wall.elasticity = 1.0
        self.wall.friction = 0.0
        self.wall.collision_type = 0
        self.space.add(self.wall)
        
    def test_ball_creation(self):
        self.assertEqual(self.ball.body.position, pymunk.Vec2d(100, 100))
        self.assertEqual(self.ball.shape.radius, 15)
        self.assertEqual(self.ball.shape.collision_type, 1)
        
    def test_angle_of_reflection(self):
        self.ball.body.position = pymunk.Vec2d(100, 150)
        
        angle = math.pi / 4
        speed = 100
        self.ball.body.velocity = pymunk.Vec2d(speed * math.cos(angle), speed * math.sin(angle))
        initial_velocity = self.ball.body.velocity.normalized()
        
        for _ in range(50):
            self.space.step(0.01)
            
            if self.ball.body.velocity.y < 0:
                break
        
        final_velocity = self.ball.body.velocity.normalized()
        
        self.assertAlmostEqual(initial_velocity.x, final_velocity.x, places=1)
        self.assertAlmostEqual(initial_velocity.y, -final_velocity.y, places=1)
        
    def test_ball_impulse(self):
        initial_velocity = pymunk.Vec2d(0, 0)
        self.assertEqual(self.ball.body.velocity, initial_velocity)
        
        impulse = pymunk.Vec2d(100, -200)
        self.ball.apply_impulse(impulse)
        
        self.space.step(0.01)
        
        self.assertGreater(self.ball.body.velocity.length, 0)
        self.assertAlmostEqual(self.ball.body.velocity.angle, impulse.angle, places=1)

if __name__ == '__main__':
    unittest.main()