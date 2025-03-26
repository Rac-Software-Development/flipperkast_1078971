import time
from game.ball import Ball
from game.bumper import Bumper

class GameManager:
    def __init__(self):
        self.ball = Ball(100, 100)
        self.bumpers = [
            Bumper(200, 250),
            Bumper(160, 160),
        ]

    def run(self):
        print("Game gestart!")
        tick = 0
        while tick < 50:
            self.ball.move()
            print(f"Bal op ({self.ball.x:.1f}, {self.ball.y:.1f})")

            for bumper in self.bumpers:
                if bumper.check_collision(self.ball):
                    bumper.on_hit()

            time.sleep(0.1)
            tick += 1
