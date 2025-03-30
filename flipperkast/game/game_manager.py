import pymunk
from game.ball import Ball
from game.flipper import Flipper
from game.bumper import Bumper
from game.plunger import Plunger
from mqtt.mqtt_client import MQTTClient
from mqtt.topics import SCORE_TOPIC, BUMPER_HIT_TOPIC, GAME_STATUS_TOPIC, BALL_POSITION_TOPIC
import math
import os
import json
import time

class GameManager:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 500.0)
        self.space.damping = 0.95
        self.space.iterations = 10
        
        self.center_x = 400
        self.center_y = 200
        self.plunger_right_x = 690
        self.arc_width = (self.plunger_right_x - self.center_x) * 2
        self.left_x = self.center_x - self.arc_width/2
        self.right_x = self.plunger_right_x
        self.bottom_y = 600
        
        flipper_center_x = self.center_x
        flipper_spread = 150
        self.left_flipper_x = flipper_center_x - flipper_spread/2
        self.right_flipper_x = flipper_center_x + flipper_spread/2
        self.flipper_y = 550
        
        self.stuck_frames_count = 0
        
        self.mqtt = MQTTClient()
        self.mqtt.start()
        
        self.create_walls()
        self.plunger = Plunger(self.space, (self.right_x - 20, 650))
        self.ball = Ball(self.space, position=(self.right_x - 20, 620), radius=15)
        self.ball_shape = self.ball.shape
        self.ball_shape.density = 0.02
        self.ball_shape.collision_type = 1
        
        self.bumpers = self.create_bumpers()
        
        self.left_flipper = Flipper(self.space, (self.left_flipper_x, self.flipper_y + 90), is_left=True)
        self.right_flipper = Flipper(self.space, (self.right_flipper_x, self.flipper_y + 90), is_left=False)  
        
        self.setup_collision_handlers()
        
        self.score = 0
        self.highscore = self.load_highscore()
        self.game_over = False
        self.quit_game = False
        self.game_started = False
        
        self.last_position_update = 0
        self.position_update_interval = 0.05
        
        self.display = None
        
        self.mqtt.publish_game_status("READY")
    
    def create_bumpers(self):
        bumpers = []
        
        bumpers.append(Bumper(self.space, 220, 250, radius=23, collision_type=98, 
                             bumper_id="top_left", mqtt_client=self.mqtt))
        bumpers.append(Bumper(self.space, 580, 250, radius=23, collision_type=98, 
                             bumper_id="top_right", mqtt_client=self.mqtt))
        bumpers.append(Bumper(self.space, 180, 350, radius=23, collision_type=98, 
                             bumper_id="left_side", mqtt_client=self.mqtt))
        bumpers.append(Bumper(self.space, 620, 350, radius=23, collision_type=98, 
                             bumper_id="right_side", mqtt_client=self.mqtt))
        bumpers.append(Bumper(self.space, self.left_x + 50, self.bottom_y - 30, radius=23, 
                            collision_type=98, bumper_id="bottom_left_corner", mqtt_client=self.mqtt))
        bumpers.append(Bumper(self.space, self.right_x - 90, self.bottom_y - 30, radius=23, 
                            collision_type=98, bumper_id="bottom_right_corner", mqtt_client=self.mqtt))
        
        return bumpers
    
    def set_display(self, display):
        self.display = display
    
    def create_walls(self):
        wall_thickness = 3.0
        
        segments = 20
        for i in range(segments):
            angle1 = math.pi + (i * math.pi / segments)
            angle2 = math.pi + ((i + 1) * math.pi / segments)
            
            x1 = self.center_x + (self.arc_width/2) * math.cos(angle1)
            y1 = self.center_y + (self.arc_width/2) * math.sin(angle1)
            x2 = self.center_x + (self.arc_width/2) * math.cos(angle2)
            y2 = self.center_y + (self.arc_width/2) * math.sin(angle2)
            
            segment = pymunk.Segment(self.space.static_body, (x1, y1), (x2, y2), wall_thickness)
            segment.elasticity = 0.7
            segment.friction = 0.5
            self.space.add(segment)
        
        left_wall = pymunk.Segment(
            self.space.static_body,
            (self.left_x, self.center_y),
            (self.left_x, self.bottom_y),
            wall_thickness
        )
        
        right_wall = pymunk.Segment(
            self.space.static_body,
            (self.right_x - 40, self.center_y),
            (self.right_x - 40, self.bottom_y),
            wall_thickness
        )
        
        bottom_left_wall = pymunk.Segment(
            self.space.static_body,
            (self.left_x, self.bottom_y),
            (self.left_flipper_x - 50, self.bottom_y),
            wall_thickness
        )
        
        bottom_right_wall = pymunk.Segment(
            self.space.static_body,
            (self.right_flipper_x + 50, self.bottom_y),
            (self.right_x - 40, self.bottom_y),
            wall_thickness
        )
        
        drain_sensor = pymunk.Segment(
            self.space.static_body,
            (self.left_flipper_x - 50, self.bottom_y),
            (self.right_flipper_x + 50, self.bottom_y),
            wall_thickness
        )
        drain_sensor.sensor = True
        drain_sensor.collision_type = 99
        
        bottom_left_diag = pymunk.Segment(
            self.space.static_body,
            (self.left_x, self.bottom_y),
            (self.left_flipper_x - 30, self.bottom_y + 50),
            wall_thickness
        )
        
        bottom_right_diag = pymunk.Segment(
            self.space.static_body,
            (self.right_x - 40, self.bottom_y),
            (self.right_flipper_x + 30, self.bottom_y + 50),
            wall_thickness
        )
        
        plunger_lane_right = pymunk.Segment(
            self.space.static_body,
            (self.right_x, self.center_y),
            (self.right_x, self.bottom_y + 150),
            wall_thickness
        )
        
        plunger_lane_bottom = pymunk.Segment(
            self.space.static_body,
            (self.right_x - 40, self.bottom_y + 150),
            (self.right_x, self.bottom_y + 150),
            wall_thickness
        )
        
        right_wall_extension = pymunk.Segment(
            self.space.static_body,
            (self.right_x - 40, self.bottom_y),
            (self.right_x - 40, self.bottom_y + 150),
            wall_thickness
        )
        
        all_walls = [
            left_wall, right_wall,
            bottom_left_wall, bottom_right_wall, drain_sensor,
            bottom_left_diag, bottom_right_diag,
            plunger_lane_right, plunger_lane_bottom, right_wall_extension
        ]
        
        for wall in all_walls:
            wall.elasticity = 0.7
            wall.friction = 0.5
            self.space.add(wall)
    
    def setup_collision_handlers(self):
        drain_handler = self.space.add_collision_handler(1, 99)
        drain_handler.post_solve = self.on_ball_drained
        
        bumper_handler = self.space.add_collision_handler(1, 98)
        bumper_handler.pre_solve = self.on_bumper_hit_pre
        bumper_handler.post_solve = self.on_bumper_hit_post
        
        plunger_handler = self.space.add_collision_handler(1, 2)
        plunger_handler.pre_solve = self.on_plunger_hit

    def on_plunger_hit(self, arbiter, space, data):
        ball_shape = arbiter.shapes[0]
        plunger_shape = arbiter.shapes[1]
        
        if ball_shape.body.position.y < plunger_shape.body.position.y:
            return True
        
        ball_shape.body.apply_impulse_at_local_point((0, -3000))
        
        if (ball_shape.body.position - plunger_shape.body.position).length < (ball_shape.radius + plunger_shape.radius):
            ball_shape.body.position = (ball_shape.body.position.x, plunger_shape.body.position.y - ball_shape.radius - plunger_shape.radius - 5)
        
        return True

    def on_bumper_hit_pre(self, arbiter, space, data):
        shapes = arbiter.shapes
        if len(shapes) != 2:
            return True
            
        ball_shape = shapes[0]
        bumper_shape = shapes[1]
        
        ball_body = ball_shape.body
        bumper_body = bumper_shape.body
        
        normal = (ball_body.position - bumper_body.position).normalized()
        velocity = ball_body.velocity
        
        dot_product = velocity.dot(normal)
        reflection = velocity - 2 * dot_product * normal
        
        extra_velocity = normal * 150
        
        ball_body.velocity = reflection + extra_velocity
        
        if not self.game_started:
            self.game_started = True
            self.mqtt.publish_game_status("STARTED")
        
        return True

    def on_bumper_hit_post(self, arbiter, space, data):
        points = 10
        
        self.score += points
        if self.display:
            self.display.update_score(points)
        
        bumper_shape = None
        for shape in arbiter.shapes:
            if shape.collision_type == 98:
                bumper_shape = shape
                break
        
        if bumper_shape:
            for bumper in self.bumpers:
                if bumper.shape == bumper_shape:
                    bumper.hit()
        
        self.mqtt.publish_score_update(points)
        
        return True
    
    def on_ball_drained(self, arbiter, space, data):
        if not self.game_over:
            self.game_over = True
            
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore(self.highscore)
            
            self.mqtt.publish_game_status("GAME_OVER", self.score)
            
            self.quit_game = True
            
            print(f"Game over! Final score: {self.score}, Highscore: {self.highscore}")
        
        return True
        
    def update(self):
        dt = 1.0 / 90.0
        for _ in range(2):
            self.check_ball_bounds()
            self.space.step(dt)
            
        for bumper in self.bumpers:
            bumper.update()
            
        current_time = time.time()
        if current_time - self.last_position_update >= self.position_update_interval:
            self.last_position_update = current_time
            self.publish_ball_position()
    
    def publish_ball_position(self):
        if self.ball_shape and hasattr(self.ball_shape, 'body'):
            position = self.ball_shape.body.position
            velocity = self.ball_shape.body.velocity
            self.mqtt.publish_ball_position(position.x, position.y, velocity.x, velocity.y)
    
    def check_ball_bounds(self):
        if self.ball_shape.body.position.y > self.bottom_y + 800 and not self.game_over:
            self.game_over = True
            
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore(self.highscore)
                
            self.mqtt.publish_game_status("GAME_OVER", self.score)
                
            self.quit_game = True
            
            print(f"Ball out of bounds! Game over. Score: {self.score}, Highscore: {self.highscore}")
            return
        
        plunger_lane_left = self.right_x - 40
        plunger_lane_right = self.right_x
        
        ball_pos = self.ball_shape.body.position
        ball_vel = self.ball_shape.body.velocity
        
        if (ball_pos.x > plunger_lane_left - 15 and ball_pos.x < plunger_lane_right + 15 and 
            ball_pos.y > self.bottom_y and ball_pos.y < self.bottom_y + 150):
            
            if abs(ball_vel.x) < 10 and abs(ball_vel.y) < 50:
                self.stuck_frames_count += 1
                
                if self.stuck_frames_count > 30:
                    self.reset_ball()
                    self.stuck_frames_count = 0
            else:
                self.stuck_frames_count = 0
                
        plunger_pos = self.plunger.body.position
        distance = ((plunger_pos.x - ball_pos.x)**2 + (plunger_pos.y - ball_pos.y)**2)**0.5
        
        if distance < 20 and ball_pos.y > plunger_pos.y:
            self.reset_ball()
    
    def launch_ball(self, power=1.0):
        if not self.game_started:
            self.game_started = True
            self.mqtt.publish_game_status("STARTED")
            
        launched = self.plunger.launch(self.ball_shape.body, power)
        
        if launched:
            self.mqtt.publish_game_status("BALL_LAUNCHED", power)
            
    def reset_ball(self):
        plunger_y = self.plunger.body.position.y
        
        self.ball_shape.body.velocity = (0, 0)
        self.ball_shape.body.angular_velocity = 0
        self.ball_shape.body.force = (0, 0)
        self.ball_shape.body.torque = 0
        
        lane_center_x = (self.right_x + (self.right_x - 40)) / 2
        
        self.ball_shape.body.position = (lane_center_x, plunger_y - 40)
        
        for _ in range(5):
            self.ball_shape.body.velocity = (0, 0)
            self.ball_shape.body.angular_velocity = 0
            
        self.mqtt.publish_game_status("BALL_RESET")
    
    def load_highscore(self):
        try:
            if os.path.exists('highscore.json'):
                with open('highscore.json', 'r') as f:
                    data = json.load(f)
                    return data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")
        
        return 0
    
    def save_highscore(self, score):
        try:
            with open('highscore.json', 'w') as f:
                json.dump({'highscore': score}, f)
            print(f"Highscore saved: {score}")
            
            self.mqtt.publish_game_status("NEW_HIGHSCORE", score)
        except Exception as e:
            print(f"Error saving highscore: {e}")
    
    def get_flippers(self):
        return [self.left_flipper, self.right_flipper]
        
    def stop(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore(self.highscore)
            
        self.mqtt.publish_game_status("STOPPED")
        self.mqtt.stop()