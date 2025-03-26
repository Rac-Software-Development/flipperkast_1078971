import unittest
from mqtt.mqtt_client import MQTTClient

class TestMQTTClient(unittest.TestCase):
    def test_can_create_client(self):
        mqtt_client = MQTTClient()
        self.assertIsNotNone(mqtt_client.client)

    def test_can_publish(self):
        mqtt_client = MQTTClient()
        try:
            mqtt_client.publish("flipperkast/test", "Test Mqtt")
            success = True
        except Exception:
            success = False
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
