import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker='broker.hivemq.com', port=1883):
        self.client = mqtt.Client()
        self.client.connect(broker, port)
    
    def publish(self, topic, message):
        print(f"MQTT -> topic: {topic} | message: {message}")
        self.client.publish(topic, message)

    def start(self):
        self.client.loop_start()
    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
