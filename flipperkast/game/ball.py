import pymunk
import math

class Ball:
    def __init__(self, space, position=(565, 650), radius=14):
        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        
        self.body = pymunk.Body(mass, inertia)
        self.body.position = position
        
        self.body.angular_damping = 0.7
        self.body.damping = 0.9
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.6
        self.shape.friction = 0.7
        
        self.shape.collision_type = 1
        
        space.add(self.body, self.shape)
        
        self.setup_collision_handlers(space)
        
    def setup_collision_handlers(self, space):
        wall_handler = space.add_collision_handler(1, 0)
        wall_handler.pre_solve = self.handle_wall_collision
        
    def handle_wall_collision(self, arbiter, space, data):
        normal = arbiter.normal
        velocity = self.body.velocity

        dot_product = velocity.dot(normal)
        reflection = velocity - 2 * dot_product * normal
        
        damping_factor = 0.9
        reflection = reflection * damping_factor
        
        self.body.velocity = reflection
        
        return True
        
    def apply_impulse(self, impulse):
        self.body.apply_impulse_at_local_point(impulse)