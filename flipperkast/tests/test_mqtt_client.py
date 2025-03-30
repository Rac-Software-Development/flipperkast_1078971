import unittest
from unittest.mock import MagicMock, patch
import json
import time
from mqtt.mqtt_client import MQTTClient
from mqtt.topics import SCORE_TOPIC, BUMPER_HIT_TOPIC, BALL_POSITION_TOPIC, GAME_STATUS_TOPIC

class TestMQTTClient(unittest.TestCase):
    @patch('paho.mqtt.client.Client')
    def setUp(self, mock_mqtt_client):
        self.mock_client = MagicMock()
        mock_mqtt_client.return_value = self.mock_client
        
        self.mqtt = MQTTClient(broker="test.broker", port=1883, client_id="test_client")
        
    def test_initialization(self):
        self.assertEqual(self.mqtt.broker, "test.broker")
        self.assertEqual(self.mqtt.port, 1883)
        self.assertEqual(self.mqtt.client_id, "test_client")
        self.assertFalse(self.mqtt.running)
        
    @patch('threading.Thread')
    def test_start(self, mock_thread):
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        self.mqtt.start()
        
        self.mock_client.connect.assert_called_once_with("test.broker", 1883, 60)
        self.assertTrue(self.mqtt.running)
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        
    def test_stop(self):
        self.mqtt.running = True
        self.mqtt.thread = MagicMock()
        
        self.mqtt.stop()
        
        self.mock_client.disconnect.assert_called_once()
        self.assertFalse(self.mqtt.running)
        self.mqtt.thread.join.assert_called_once()
        
    def test_publish(self):
        self.mqtt.running = True
        self.mock_client.publish.return_value.rc = 0
        
        result = self.mqtt.publish("test/topic", "test_message")
        
        self.assertTrue(result)
        self.mock_client.publish.assert_called_once_with("test/topic", "test_message")
        
    def test_publish_dict(self):
        self.mqtt.running = True
        self.mock_client.publish.return_value.rc = 0
        
        data = {"key": "value", "number": 42}
        result = self.mqtt.publish("test/topic", data)
        
        self.assertTrue(result)
        self.mock_client.publish.assert_called_once_with("test/topic", json.dumps(data))
        
    def test_publish_score_update(self):
        self.mqtt.running = True
        self.mqtt.publish = MagicMock(return_value=True)
        
        points = 42
        result = self.mqtt.publish_score_update(points)
        
        self.assertTrue(result)
        self.mqtt.publish.assert_called_once_with(SCORE_TOPIC, str(points))
        
    def test_publish_bumper_hit(self):
        self.mqtt.running = True
        self.mqtt.publish = MagicMock(return_value=True)
        
        bumper_id = "test_bumper"
        points = 10
        
        with patch('time.time', return_value=12345):
            result = self.mqtt.publish_bumper_hit(bumper_id, points)
            
            self.assertTrue(result)
            expected_data = {
                "id": bumper_id,
                "points": points,
                "timestamp": 12345
            }
            self.mqtt.publish.assert_called_once_with(BUMPER_HIT_TOPIC, expected_data)
            
    def test_publish_ball_position(self):
        self.mqtt.running = True
        self.mqtt.publish = MagicMock(return_value=True)
        
        x, y = 100, 200
        vx, vy = 10, -20
        
        with patch('time.time', return_value=12345):
            result = self.mqtt.publish_ball_position(x, y, vx, vy)
            
            self.assertTrue(result)
            expected_data = {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "timestamp": 12345
            }
            self.mqtt.publish.assert_called_once_with(BALL_POSITION_TOPIC, expected_data)
            
    def test_publish_game_status(self):
        self.mqtt.running = True
        self.mqtt.publish = MagicMock(return_value=True)
        
        status = "GAME_OVER"
        value = 100
        
        with patch('time.time', return_value=12345):
            result = self.mqtt.publish_game_status(status, value)
            
            self.assertTrue(result)
            expected_data = {
                "status": status,
                "value": value,
                "timestamp": 12345
            }
            self.mqtt.publish.assert_called_once_with(GAME_STATUS_TOPIC, expected_data)
            
    def test_subscribe(self):
        self.mqtt.running = True
        self.mock_client.subscribe.return_value = (0, None)
        
        callback = MagicMock()
        result = self.mqtt.subscribe("test/topic", callback)
        
        self.assertTrue(result)
        self.mock_client.subscribe.assert_called_once_with("test/topic")
        self.assertEqual(len(self.mqtt.subscribed_topics), 1)
        self.assertEqual(self.mqtt.subscribed_topics[0], "test/topic")
        self.assertEqual(len(self.mqtt.topic_callbacks["test/topic"]), 1)
        self.assertEqual(self.mqtt.topic_callbacks["test/topic"][0], callback)

if __name__ == '__main__':
    unittest.main()