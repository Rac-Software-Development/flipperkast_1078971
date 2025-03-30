import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import time
from pygame.locals import *

class Display:
    def __init__(self, space, ball_shape, flippers=None, bumpers=None, plunger=None):
        pygame.init()
        self.width, self.height = 800, 750
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Flipperkast Simulator")
        
        self.clock = pygame.time.Clock()
        
        self.space = space
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        
        self.ball_shape = ball_shape
        self.flippers = flippers or []
        self.bumpers = bumpers or []
        self.plunger = plunger
        
        self.wall_segments = []
        self.extract_wall_segments()
        
        self.background_color = (222, 222, 222)
        self.outline_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        
        self.left_flipper_activated = False
        self.right_flipper_activated = False
        
        self.plunger_compression = 0
        self.is_plunger_held = False
        
        self.score = 0
        
        self.game_over_delay = 5.0
        self.game_over_time = 0
    
    def extract_wall_segments(self):
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Segment):
                if shape.body.body_type == pymunk.Body.STATIC:
                    if not hasattr(shape, 'sensor') or not shape.sensor:
                        self.wall_segments.append(shape)
    
    def handle_events(self, game_manager):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                
                elif event.key in (K_LEFT, K_z, K_a):
                    if not self.left_flipper_activated and self.flippers and len(self.flippers) > 0:
                        self.flippers[0].activate()
                        self.left_flipper_activated = True
                
                elif event.key in (K_RIGHT, K_m, K_l):
                    if not self.right_flipper_activated and self.flippers and len(self.flippers) > 1:
                        self.flippers[1].activate()
                        self.right_flipper_activated = True
                
                elif event.key == K_SPACE:
                    if not game_manager.game_over:
                        self.is_plunger_held = True
            
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_z, K_a):
                    if self.left_flipper_activated and self.flippers and len(self.flippers) > 0:
                        self.flippers[0].deactivate()
                        self.left_flipper_activated = False
                
                elif event.key in (K_RIGHT, K_m, K_l):
                    if self.right_flipper_activated and self.flippers and len(self.flippers) > 1:
                        self.flippers[1].deactivate()
                        self.right_flipper_activated = False
                
                elif event.key == K_SPACE:
                    if self.is_plunger_held and self.plunger and not game_manager.game_over:
                        power = min(1.0, self.plunger_compression / self.plunger.max_compression)
                        game_manager.launch_ball(power)
                    self.is_plunger_held = False
                    self.plunger_compression = 0
        
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and self.is_plunger_held and self.plunger and not game_manager.game_over:
            self.plunger_compression = min(self.plunger.max_compression, self.plunger_compression + 2)
            self.plunger.compress(self.plunger_compression)
        
        if game_manager.quit_game:
            if self.game_over_time == 0:
                self.game_over_time = time.time()
            
            current_time = time.time()
            if current_time - self.game_over_time >= self.game_over_delay:
                return False
        
        return True
    
    def draw_elements(self, game_manager):
        self.screen.fill(self.background_color)
        
        self.draw_walls()
        
        for bumper in self.bumpers:
            bumper.draw(self.screen)
        
        for flipper in self.flippers:
            flipper.draw(self.screen)
        
        if self.plunger:
            self.plunger.draw(self.screen)
        
        self.draw_ball()
        
        self.draw_score(game_manager.highscore)
        
        if game_manager.game_over:
            self.draw_game_over(game_manager.score, game_manager.highscore)
        
        self.draw_controls(game_manager.game_over)
    
    def draw_walls(self):
        line_thickness = 3
        
        for wall in self.wall_segments:
            p1 = wall.a
            p2 = wall.b
            
            if abs(p1.y - 600) < 5 and abs(p2.y - 600) < 5:
                continue
            
            pygame.draw.line(
                self.screen, 
                self.outline_color,
                (int(p1.x), int(p1.y)),
                (int(p2.x), int(p2.y)),
                line_thickness
            )
    
    def draw_ball(self):
        if hasattr(self, 'ball_shape') and self.ball_shape and hasattr(self.ball_shape, 'body'):
            pos = self.ball_shape.body.position
            radius = self.ball_shape.radius
            
            pygame.draw.circle(self.screen, (80, 180, 80), 
                              (int(pos.x), int(pos.y)), int(radius))
    
    def draw_score(self, highscore):
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, self.text_color)
        self.screen.blit(score_surface, (20, 20))
        
        highscore_text = f"Highscore: {highscore}"
        highscore_surface = self.font.render(highscore_text, True, self.text_color)
        self.screen.blit(highscore_surface, (self.width - highscore_surface.get_width() - 20, 20))
    
    def draw_game_over(self, final_score, highscore):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(game_over_text, 
                         (self.width//2 - game_over_text.get_width()//2, 
                          self.height//2 - 100))
        
        final_score_text = self.font.render(f"Final Score: {final_score}", True, (255, 255, 255))
        self.screen.blit(final_score_text, 
                         (self.width//2 - final_score_text.get_width()//2, 
                          self.height//2 - 30))
        
        if final_score >= highscore:
            highscore_text = self.font.render(f"NEW HIGHSCORE!", True, (255, 215, 0))
        else:
            highscore_text = self.font.render(f"Highscore: {highscore}", True, (255, 255, 255))
        
        self.screen.blit(highscore_text, 
                         (self.width//2 - highscore_text.get_width()//2, 
                          self.height//2 + 20))
        
        seconds_left = max(0, int(self.game_over_delay - (time.time() - self.game_over_time)))
        if seconds_left > 0:
            quit_text = self.small_font.render(f"Spel sluit over {seconds_left} seconden...", True, (200, 200, 200))
            self.screen.blit(quit_text, 
                            (self.width//2 - quit_text.get_width()//2, 
                            self.height//2 + 80))
    
    def draw_controls(self, game_over=False):
        controls_font = pygame.font.SysFont("Arial", 16)
        
        if game_over:
            controls_text = controls_font.render(
                "Game Over - Het spel sluit automatisch", 
                True, (180, 180, 180))
        else:
            controls_text = controls_font.render(
                "Controls: A/Z/Left, L/M/Right voor flippers, Space voor plunger, ESC om te stoppen", 
                True, (80, 80, 80))
            
        self.screen.blit(controls_text, 
                         (self.width//2 - controls_text.get_width()//2, self.height - 30))
    
    def update_score(self, points):
        self.score += points
        print(f"Score updated: +{points}, total: {self.score}")
    
    def run(self, game_manager):
        running = True
        fps = 60
        
        game_manager.set_display(self)
        
        while running:
            running = self.handle_events(game_manager)
            
            if not game_manager.game_over:
                game_manager.update()
            
            self.draw_elements(game_manager)
            
            pygame.display.flip()
            
            self.clock.tick(fps)
        
        pygame.quit()
        sys.exit()