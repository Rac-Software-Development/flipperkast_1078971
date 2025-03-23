class Bumper:
    def __init__(self, x: float, y: float, radius: float = 15, score_value: int = 100):
        self.x = x
        self.y = y
        self.radius = radius
        self.score_value = score_value

    def check_collision(self, ball):
        dx = self.x - ball.x
        dy = self.y - ball.y
        distance_squared = dx ** 2 + dy ** 2
        return distance_squared <= self.radius ** 2

    def on_hit(self):
        pass