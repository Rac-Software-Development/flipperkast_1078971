import math
import pygame
import pymunk

class Flipper:
    def __init__(self, space, position, is_left):
        self.space = space
        self.is_left = is_left
        
        width, height = 100, 20
        mass = 3
        moment = pymunk.moment_for_box(mass, (width, height))
        
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.body.angle = 0.0
        
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.elasticity = 0.8
        self.shape.friction = 0.2
        self.shape.collision_type = 4
        self.space.add(self.body, self.shape)
        
        pivot_offset = (-width / 2, 0) if is_left else (width / 2, 0)
        pivot_world = self.body.position + pivot_offset
        self.pivot = pymunk.PivotJoint(self.space.static_body, self.body, pivot_world)
        self.pivot.collide_bodies = False
        self.space.add(self.pivot)
        
        rest_angle = 0.3 if is_left else -0.3
        angle_range = math.radians(60)

        if is_left:
            min_angle = rest_angle - angle_range
            max_angle = rest_angle
            self.target_angle = min_angle
        else:
            min_angle = rest_angle
            max_angle = rest_angle + angle_range
            self.target_angle = max_angle
            
        self.limit_joint = pymunk.RotaryLimitJoint(self.space.static_body, self.body, min_angle, max_angle)
        space.add(self.limit_joint)
        
        self.spring = pymunk.DampedRotarySpring(
            self.space.static_body, self.body, rest_angle,
            stiffness=3000000,
            damping=20000
        )
        self.space.add(self.spring)
        
        self.motor = pymunk.SimpleMotor(self.space.static_body, self.body, 0)
        self.motor.max_force = 5000000
        self.motor_active = False
        
        self.setup_collision_handler(space)
    
    def setup_collision_handler(self, space):
        handler = space.add_collision_handler(4, 1)
        handler.pre_solve = self.on_ball_hit
    
    def on_ball_hit(self, arbiter, space, data):
        if self.motor_active:
            shapes = arbiter.shapes
            ball_shape = shapes[1] if shapes[0].collision_type == 4 else shapes[0]
            flipper_shape = shapes[0] if shapes[0].collision_type == 4 else shapes[1]
            
            ball_body = ball_shape.body
            flipper_body = flipper_shape.body
            
            collision_point = arbiter.contact_point_set.points[0].point_a

            flipper_velocity = flipper_body.velocity_at_world_point(collision_point)

            direction_x = 1.0 if self.is_left else -1.0
            direction = pymunk.Vec2d(direction_x, -3.0).normalized()
            
            flipper_speed = flipper_velocity.length
            impulse_strength = 500 + flipper_speed * 0.8
            

            impulse = direction * impulse_strength
            ball_body.apply_impulse_at_local_point(impulse)
        
        return True
    
    def activate(self):
        if not self.motor_active:
            self.motor_active = True
            rate = 20 if self.is_left else -20
            self.motor.rate = rate
            self.space.add(self.motor)
    
    def deactivate(self):
        if self.motor_active:
            self.motor_active = False
            self.space.remove(self.motor)
    
    def draw(self, screen):
        vertices = [self.body.local_to_world(v) for v in self.shape.get_vertices()]
        points = [(int(v.x), int(v.y)) for v in vertices]
        
        pygame.draw.polygon(screen, (130, 130, 130), points)
        if self.motor_active:
            pygame.draw.polygon(screen, (160, 160, 160), points, 2)