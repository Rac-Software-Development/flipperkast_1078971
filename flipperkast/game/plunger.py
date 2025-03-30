import pymunk
import pygame
import math

class Plunger:
    def __init__(self, space, position):
        self.space = space
        self.position = position
        self.compression = 0
        self.max_compression = 50
        self.spring_constant = 500.0
        
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = position
        
        self.shape = pymunk.Circle(self.body, 20)
        self.shape.collision_type = 2
        self.shape.elasticity = 0.6
        
        self.sensor = pymunk.Circle(self.body, 30)
        self.sensor.sensor = True
        self.sensor.collision_type = 3
        
        self.space.add(self.body, self.shape, self.sensor)
        
        handler = space.add_collision_handler(1, 3)
        handler.separate = self.on_ball_separate_from_sensor
    
    def on_ball_separate_from_sensor(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0] if arbiter.shapes[0].collision_type == 1 else arbiter.shapes[1]
        
        if ball_shape.body.position.y > self.body.position.y and ball_shape.body.velocity.y > 0:
            ball_shape.body.position = (ball_shape.body.position.x, self.body.position.y - 30)
            ball_shape.body.velocity = (ball_shape.body.velocity.x, -100)
        
        return True
    
    def compress(self, amount):
        self.compression = min(self.max_compression, amount)
        self.body.position = (self.position[0], self.position[1] + self.compression)
    
    def launch(self, ball_body, power=1.0):
        if self.compression > 0:
            force = self.spring_constant * self.compression * power
            
            ball_body.velocity = (0, 0)
            ball_body.angular_velocity = 0
            
            current_pos = ball_body.position
            correct_y = self.position[1] - 40
            ball_body.position = (current_pos.x, correct_y)
            
            for _ in range(2):
                ball_body.velocity = (0, 0)
            
            impulse = (0, -force)
            ball_body.apply_impulse_at_local_point(impulse)
            
            self.compression = 0
            self.body.position = self.position
            return True
        return False
    
    def draw(self, screen):
        start_pos = (self.position[0], self.position[1] + self.max_compression)
        end_pos = (self.position[0], self.position[1] + self.compression)
        
        pygame.draw.line(screen, (100, 100, 100), start_pos, end_pos, 6)
        
        pygame.draw.circle(
            screen,
            (150, 150, 150),
            (int(self.body.position.x), int(self.body.position.y)),
            20
        )