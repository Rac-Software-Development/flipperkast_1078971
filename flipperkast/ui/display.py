import pygame
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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

        self.left_angle = 0
        self.right_angle = 0

    def draw_flipper(self, pivot, length, width, angle, flip=False):
        short = width // 2
        long = width

        points = [
            (pivot[0], pivot[1]),
            (pivot[0] + length, pivot[1] - short),
            (pivot[0] + length, pivot[1] + short),
        ]

        if flip:
            points = [(2 * pivot[0] - x, y) for (x, y) in points]

        rotated = [rotate_point(p, pivot, angle) for p in points]
        pygame.draw.polygon(self.screen, (255, 80, 80), rotated)

    def draw(self):
        self.screen.fill((0, 0, 0))

        wall_thickness = 10
        wall_color = (100, 100, 100)
        pygame.draw.rect(self.screen, wall_color, (0, 0, wall_thickness, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, wall_color, (SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, wall_color, (0, 0, SCREEN_WIDTH, wall_thickness))
        pygame.draw.rect(self.screen, wall_color, (0, SCREEN_HEIGHT - wall_thickness, 260, wall_thickness))
        pygame.draw.rect(self.screen, wall_color, (SCREEN_WIDTH - 260, SCREEN_HEIGHT - wall_thickness, 260, wall_thickness))

        pygame.draw.circle(self.screen, (255, 255, 255), (int(self.ball.x), int(self.ball.y)), BALL_RADIUS)

        for bumper in self.bumpers:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(bumper.x), int(bumper.y)), bumper.radius)

        self.draw_flipper(pivot=(280, 540), length=100, width=20, angle=self.left_angle, flip=False)
        self.draw_flipper(pivot=(520, 540), length=100, width=20, angle=self.right_angle, flip=True)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            self.left_angle = 60 if keys[pygame.K_a] else 0
            self.right_angle = -60 if keys[pygame.K_l] else 0

            self.ball.move()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
