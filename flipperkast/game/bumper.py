import pymunk
import pygame
import random
import math
from mqtt.mqtt_client import MQTTClient
from mqtt.topics import BUMPER_HIT_TOPIC

class Bumper:
    def __init__(self, space, x, y, radius=20, collision_type=3, bumper_id=None, mqtt_client=None):
        self.space = space
        self.position = (x, y)
        self.radius = radius
        self.color = (31, 163, 5, 255)
        self.highlight_color = (0, 255, 0, 255)
        self.is_hit = False
        self.hit_time = 0
        self.bumper_id = bumper_id or f"bumper_{x}_{y}"
        self.points = 10
        
        self.mqtt_client = mqtt_client
        
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 1.2
        self.shape.friction = 0.3
        self.shape.collision_type = collision_type
        
        self.shape.bumper = self
        
        space.add(self.body, self.shape)
        self.setup_collision_handlers(space)
        
    def setup_collision_handlers(self, space):
        pass
        
    def handle_collision(self, ball_body):
        ball_pos = ball_body.position
        bumper_pos = self.body.position
        normal = (ball_pos - bumper_pos).normalized()
        velocity = ball_body.velocity
        dot_product = velocity.dot(normal)
        reflection = velocity - 2 * dot_product * normal
        
        extra_velocity = normal * 150
        ball_body.velocity = reflection + extra_velocity
        
        points = self.hit()
        
        self.publish_hit(points)
        
        return points
        
    def hit(self):
        self.is_hit = True
        self.hit_time = 10
        
        jitter_x = random.uniform(-1.5, 1.5)
        jitter_y = random.uniform(-1.5, 1.5)
        self.body.position = (self.position[0] + jitter_x, self.position[1] + jitter_y)
        
        return self.points
        
    def publish_hit(self, points):
        if self.mqtt_client:
            self.mqtt_client.publish_bumper_hit(self.bumper_id, points)
        
    def update(self):
        if self.is_hit:
            self.hit_time -= 1
            if self.hit_time <= 0:
                self.is_hit = False
                self.body.position = self.position
                
    def draw(self, screen):
        color = self.highlight_color if self.is_hit else self.color
        
        pygame.draw.circle(
            screen,
            color,
            (int(self.body.position.x), int(self.body.position.y)),
            self.radius
        )
        
        inner_color = tuple(min(c + 50, 255) for c in color[:3]) + (color[3],)
        pygame.draw.circle(
            screen,
            inner_color,
            (int(self.body.position.x), int(self.body.position.y)),
            int(self.radius * 0.7)
        )
        
        if self.is_hit:
            pygame.draw.circle(
                screen,
                (255, 255, 255, 150),
                (int(self.body.position.x), int(self.body.position.y)),
                int(self.radius * 0.3)
            )