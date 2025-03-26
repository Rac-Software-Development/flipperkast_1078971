from mqtt.mqtt_client import MQTTClient
from mqtt.topics import SCORE_TOPIC
class ScorePanel:
    def __init__(self):
        self.scores = {"Player": 0}
        self.highscore = 0
        self.mqtt = MQTTClient()
        self.mqtt.client.on_message = self.on_message
        self.mqtt.client.subscribe(SCORE_TOPIC)
        self.mqtt.start()

    def on_message(self, client, userdata, msg):
        score = int(msg.payload.decode())
        self.scores["Player"] += score

        if self.scores["Player"] > self.highscore:
            self.highscore = self.scores["Player"]

        print(f"Score: {self.scores['Player']} |Highscore: {self.highscore}")
