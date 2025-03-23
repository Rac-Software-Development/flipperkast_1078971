class Flipper:
    def __init__(self, side: str):
        self.side = side
        self.angle = 0
        self.active = False

    def activate(self):
        self.active = True
        self.angle = 30 if self.side == 'left' else -30  # voorbeeldhoek

    def deactivate(self):
        self.active = False
        self.angle = 0

    def hit_ball(self, ball):
        if self.active:
            ball.velocity_y = -abs(ball.velocity_y)
            if self.side == 'left':
                ball.velocity_x -= 2
            else:
                ball.velocity_x += 2