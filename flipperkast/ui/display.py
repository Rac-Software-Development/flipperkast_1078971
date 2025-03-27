import pygame
import math
from game.flipper import Flipper

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
BALL_RADIUS = 10

def rotate_point(point, pivot, angle):
    angle_rad = math.radians(angle)
    x, y = point
    ox, oy = pivot
    dx, dy = x - ox, y - oy
    qx = ox + math.cos(angle_rad) * dx - math.sin(angle_rad) * dy
    qy = oy + math.sin(angle_rad) * dx + math.cos(angle_rad) * dy
    return (qx, qy)

class Display:
    def __init__(self, ball, bumpers=[]):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FlipperkastWP")
        self.clock = pygame.time.Clock()
        self.ball = ball
        self.bumpers = bumpers

        self.left_flipper = None
        self.right_flipper = None

        self.left_angle = 0
        self.right_angle = 0

    def set_flippers(self, left_flipper, right_flipper):
        self.left_flipper = left_flipper
        self.right_flipper = right_flipper

    def draw_flipper(self, flipper, pivot, length, width, flip=False):
        short = width // 2
        points = [
            (pivot[0], pivot[1]),
            (pivot[0] + length, pivot[1] - short),
            (pivot[0] + length, pivot[1] + short),
        ]

        if flip:
            points = [(2 * pivot[0] - x, y) for (x, y) in points]

        rotated = [rotate_point(p, pivot, flipper.angle) for p in points]
        pygame.draw.polygon(self.screen, (255, 80, 80), rotated)

    def draw(self):
        self.screen.fill((0, 0, 0))

        wall_thickness = 10
        wall_color = (100, 100, 100)
        pygame.draw.rect(self.screen, wall_color, (0, 0, wall_thickness, SCREEN_HEIGHT))  # links
        pygame.draw.rect(self.screen, wall_color, (SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT))  # rechts
        pygame.draw.rect(self.screen, wall_color, (0, 0, SCREEN_WIDTH, wall_thickness))  # boven
        pygame.draw.rect(self.screen, wall_color, (0, SCREEN_HEIGHT - wall_thickness, 140, wall_thickness))  # onderlinks
        pygame.draw.rect(self.screen, wall_color, (SCREEN_WIDTH - 140, SCREEN_HEIGHT - wall_thickness, 140, wall_thickness))  # onderrechts

        pygame.draw.circle(self.screen, (255, 255, 255), (int(self.ball.x), int(self.ball.y)), BALL_RADIUS)

        for bumper in self.bumpers:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(bumper.x), int(bumper.y)), bumper.radius)

        self.draw_flipper(self.left_flipper, pivot=(180, 740), length=100, width=20)
        self.draw_flipper(self.right_flipper, pivot=(420, 740), length=100, width=20, flip=True)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            if self.left_flipper:
                if keys[pygame.K_a]:
                    self.left_flipper.activate()
                else:
                    self.left_flipper.deactivate()

            if self.right_flipper:
                if keys[pygame.K_l]:
                    self.right_flipper.activate()
                else:
                    self.right_flipper.deactivate()

            self.ball.move()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
