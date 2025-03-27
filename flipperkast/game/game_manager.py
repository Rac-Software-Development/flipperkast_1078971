import time
from game.ball import Ball
from game.bumper import Bumper
from game.flipper import Flipper
from mqtt.mqtt_client import MQTTClient

class GameManager:
    def __init__(self):
        self.ball = Ball(100, 100)
        self.bumpers = [
            Bumper(200, 250),
            Bumper(160, 160),
        ]
        self.left_flipper = Flipper("left")
        self.right_flipper = Flipper("right")
        self.mqtt = MQTTClient()
        self.mqtt.start()

    def run(self):
        for _ in range(50):
            self.ball.move()
            for bumper in self.bumpers:
                if bumper.check_collision(self.ball):
                    bumper.on_hit()

            self.left_flipper.hit_ball(self.ball)
            self.right_flipper.hit_ball(self.ball)

        self.mqtt.stop()
