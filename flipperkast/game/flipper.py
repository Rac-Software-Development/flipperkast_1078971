import math
class Flipper:
    def __init__(self, side: str):
        self.side = side
        self.angle = 0
        self.active = False
        self.pivot_x = 280 if side == "left" else 520
        self.pivot_y = 540

    def activate(self):
        self.active = True
        self.angle = 30 if self.side == 'left' else -30

    def deactivate(self):
        self.active = False
        self.angle = 0

    def hit_ball(self, ball):
        dx = ball.x - self.pivot_x
        dy = ball.y - self.pivot_y
        distance = math.hypot(dx, dy)

        if distance < 50 and self.active:
            ball.velocity_y = -abs(ball.velocity_y)
            if self.side == 'left':
                ball.velocity_x -= 2
            else:
                ball.velocity_x += 2