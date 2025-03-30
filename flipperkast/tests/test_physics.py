import unittest
import pymunk
import math
from game.ball import Ball
from game.bumper import Bumper

class TestPinballPhysics(unittest.TestCase):
    def setUp(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 500)
        self.ball = Ball(self.space, position=(300, 300), radius=15)
        
        self.wall = pymunk.Segment(self.space.static_body, (200, 400), (400, 400), 5)
        self.wall.elasticity = 0.7
        self.wall.friction = 0.5
        self.wall.collision_type = 0
        self.space.add(self.wall)
        
        self.bumper = Bumper(self.space, 300, 200, radius=20, collision_type=98)
        
    def test_angle_of_incidence_equals_angle_of_reflection(self):
        angle = math.pi / 4
        speed = 200
        
        self.ball.body.position = pymunk.Vec2d(300, 350)
        self.ball.body.velocity = pymunk.Vec2d(speed * math.cos(angle), speed * math.sin(angle))
        
        initial_velocity = self.ball.body.velocity.normalized()
        initial_angle = math.atan2(initial_velocity.y, initial_velocity.x)
        
        for _ in range(30):
            self.space.step(0.01)
            
            if self.ball.body.position.y > 400:
                continue
                
            if abs(self.ball.body.velocity.y) > 0 and self.ball.body.velocity.y < 0:
                final_velocity = self.ball.body.velocity.normalized()
                final_angle = math.atan2(final_velocity.y, final_velocity.x)
                
                incidence_angle = abs(initial_angle - math.pi/2)
                reflection_angle = abs(final_angle + math.pi/2)
                
                self.assertAlmostEqual(incidence_angle, reflection_angle, delta=0.3)
                return
                
        self.fail("Ball did not reflect off the wall within the time limit")
        
    def test_bumper_collision_adds_velocity(self):
        self.ball.body.position = pymunk.Vec2d(300, 210)
        self.ball.body.velocity = pymunk.Vec2d(0, 50)
        
        initial_speed = self.ball.body.velocity.length
        
        for _ in range(200):
            self.space.step(0.01)
            
            ball_pos = self.ball.body.position
            bumper_pos = self.bumper.body.position
            distance = (ball_pos - bumper_pos).length
            
            if distance < (self.ball.shape.radius + self.bumper.radius):
                post_collision_speed = self.ball.body.velocity.length
                self.assertGreater(post_collision_speed, initial_speed)
                return
        
        print(f"Ball position: {self.ball.body.position}, Bumper position: {self.bumper.body.position}")
        print(f"Distance: {(self.ball.body.position - self.bumper.body.position).length}")
        print(f"Minimum distance needed: {self.ball.shape.radius + self.bumper.radius}")
        
        self.fail("Ball did not collide with bumper within the time limit")
        
    def test_gravity_affects_ball(self):
        self.ball.body.position = pymunk.Vec2d(300, 100)
        self.ball.body.velocity = pymunk.Vec2d(0, 0)
        
        initial_y = self.ball.body.position.y
        
        for _ in range(10):
            self.space.step(0.1)
            
        self.assertGreater(self.ball.body.position.y, initial_y)
        self.assertGreater(self.ball.body.velocity.y, 0)

if __name__ == '__main__':
    unittest.main()