class Bumper:
    def __init__(self, x: float, y: float, score_value: int = 100):
        self.x = x
        self.y = y
        self.score_value = score_value

    def on_hit(self):

