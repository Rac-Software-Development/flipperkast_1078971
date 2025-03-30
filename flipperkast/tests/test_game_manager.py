import unittest
from unittest.mock import MagicMock, patch
import pymunk
import json
import os
from game.game_manager import GameManager

class TestGameManager(unittest.TestCase):
    @patch('mqtt.mqtt_client.MQTTClient')
    def setUp(self, mock_mqtt_client):
        self.mock_mqtt = MagicMock()
        mock_mqtt_client.return_value = self.mock_mqtt
        
        self.mock_mqtt.publish_game_status = MagicMock()
        self.mock_mqtt.publish_ball_position = MagicMock()
        self.mock_mqtt.publish_score_update = MagicMock()
        self.mock_mqtt.start = MagicMock()
        
        with patch('game.bumper.Bumper') as mock_bumper, \
             patch('game.ball.Ball') as mock_ball, \
             patch('game.flipper.Flipper') as mock_flipper, \
             patch('game.plunger.Plunger') as mock_plunger, \
             patch('os.path.exists', return_value=False):
            
            self.game_manager = GameManager()
            self.game_manager.mqtt = self.mock_mqtt
            
            self.mock_ball_shape = MagicMock()
            self.mock_ball_body = MagicMock()
            self.mock_ball_shape.body = self.mock_ball_body
            self.game_manager.ball_shape = self.mock_ball_shape
    
    def test_initialization(self):
        self.assertIsNotNone(self.game_manager.space)
        self.assertEqual(self.game_manager.space.gravity, pymunk.Vec2d(0.0, 500.0))
        self.assertEqual(self.game_manager.score, 0)
        self.assertEqual(self.game_manager.highscore, 0)
        self.assertFalse(self.game_manager.game_over)
        self.assertFalse(self.game_manager.quit_game)
        self.assertFalse(self.game_manager.game_started)
        
        
    def test_create_bumpers(self):
        self.assertEqual(len(self.game_manager.bumpers), 6)
        
    def test_publish_ball_position(self):
        self.mock_ball_body.position = pymunk.Vec2d(100, 200)
        self.mock_ball_body.velocity = pymunk.Vec2d(10, -20)
        
        self.game_manager.publish_ball_position()
        
        self.mock_mqtt.publish_ball_position.assert_called_once_with(100, 200, 10, -20)
        
    @patch('json.dump')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_highscore(self, mock_open, mock_json_dump):
        score = 100
        
        self.game_manager.save_highscore(score)
        
        mock_open.assert_called_once_with('highscore.json', 'w')
        mock_json_dump.assert_called_once_with({'highscore': score}, mock_open())
        self.mock_mqtt.publish_game_status.assert_called_with("NEW_HIGHSCORE", score)
        
    def test_on_bumper_hit_post(self):
        mock_arbiter = MagicMock()
        mock_arbiter.shapes = [MagicMock(), MagicMock()]
        mock_arbiter.shapes[1].collision_type = 98
        
        mock_bumper = MagicMock()
        mock_bumper.shape = mock_arbiter.shapes[1]
        self.game_manager.bumpers = [mock_bumper]
        
        self.game_manager.display = MagicMock()
        
        result = self.game_manager.on_bumper_hit_post(mock_arbiter, None, None)
        
        self.assertTrue(result)
        self.assertEqual(self.game_manager.score, 10)
        self.game_manager.display.update_score.assert_called_once_with(10)
        mock_bumper.hit.assert_called_once()
        self.mock_mqtt.publish_score_update.assert_called_once_with(10)
        
    def test_on_ball_drained(self):
        mock_arbiter = MagicMock()
        
        result = self.game_manager.on_ball_drained(mock_arbiter, None, None)
        
        self.assertTrue(result)
        self.assertTrue(self.game_manager.game_over)
        self.assertTrue(self.game_manager.quit_game)
        self.mock_mqtt.publish_game_status.assert_called_with("GAME_OVER", 0)
        
    def test_launch_ball(self):
        self.game_manager.plunger = MagicMock()
        self.game_manager.plunger.launch.return_value = True
        
        self.game_manager.launch_ball(0.8)
        
        self.assertTrue(self.game_manager.game_started)
        self.game_manager.plunger.launch.assert_called_once_with(
            self.mock_ball_shape.body, 0.8)
        self.mock_mqtt.publish_game_status.assert_any_call("STARTED")
        self.mock_mqtt.publish_game_status.assert_called_with("BALL_LAUNCHED", 0.8)

if __name__ == '__main__':
    unittest.main()