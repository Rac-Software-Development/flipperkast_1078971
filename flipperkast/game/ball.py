class Ball:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.velocity_x = 2
        self.velocity_y = 3

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def check_collision(self, obj):
        pass