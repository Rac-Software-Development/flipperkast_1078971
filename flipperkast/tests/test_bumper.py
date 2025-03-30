import unittest
from unittest.mock import MagicMock, patch
import pymunk
from game.bumper import Bumper
from game.ball import Ball

class TestBumper(unittest.TestCase):
    def setUp(self):
        self.space = pymunk.Space()
        self.mqtt_client = MagicMock()
        self.bumper = Bumper(self.space, 100, 100, radius=20, collision_type=98, 
                            bumper_id="test_bumper", mqtt_client=self.mqtt_client)
        self.ball = Ball(self.space, position=(50, 50), radius=15)
        
    def test_bumper_creation(self):
        self.assertEqual(self.bumper.body.position, pymunk.Vec2d(100, 100))
        self.assertEqual(self.bumper.radius, 20)
        self.assertEqual(self.bumper.bumper_id, "test_bumper")
        self.assertEqual(self.bumper.shape.collision_type, 98)
        
    def test_bumper_hit(self):
        points = self.bumper.hit()
        
        self.assertEqual(points, 10)
        self.assertTrue(self.bumper.is_hit)
        self.assertEqual(self.bumper.hit_time, 10)
        
    def test_bumper_update(self):
        self.bumper.hit()
        self.assertTrue(self.bumper.is_hit)
        
        for _ in range(10):
            self.bumper.update()
            
        self.assertFalse(self.bumper.is_hit)
        self.assertEqual(self.bumper.body.position, pymunk.Vec2d(100, 100))
        
    def test_bumper_mqtt_hit_publish(self):
        points = 10
        self.bumper.publish_hit(points)
        
        self.mqtt_client.publish_bumper_hit.assert_called_once_with(
            "test_bumper", 10)
            
    def test_bumper_handle_collision(self):
        ball_body = self.ball.body
        original_ball_pos = pymunk.Vec2d(80, 80)
        ball_body.position = original_ball_pos
        
        velocity = pymunk.Vec2d(100, 100)
        ball_body.velocity = velocity
        
        points = self.bumper.handle_collision(ball_body)
        
        self.assertEqual(points, 10)
        self.assertTrue(self.bumper.is_hit)
        self.mqtt_client.publish_bumper_hit.assert_called_once()
        
        new_velocity = ball_body.velocity
        self.assertNotEqual(velocity, new_velocity)
        self.assertGreater(new_velocity.length, velocity.length)

if __name__ == '__main__':
    unittest.main()