import paho.mqtt.client as mqtt
import time
import threading
import json

from mqtt.topics import SCORE_TOPIC, BUMPER_HIT_TOPIC, BALL_POSITION_TOPIC, GAME_STATUS_TOPIC

class MQTTClient:
    def __init__(self, broker="broker.hivemq.com", port=1883, client_id=None):
        self.client_id = client_id or f"pinball_client_{int(time.time())}"
        
        self.client = mqtt.Client(client_id=self.client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.broker = broker
        self.port = port
        
        self.subscribed_topics = []
        self.topic_callbacks = {}
        
        self.running = False
        self.thread = None
        
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 12
        
        self.last_ball_position = {"x": 0, "y": 0, "vx": 0, "vy": 0}
        self.ball_position_update_interval = 50
        self.last_position_update_time = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"MQTT Connected to {self.broker} successfully")
            for topic in self.subscribed_topics:
                client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        else:
            print(f"MQTT Connection failed with code {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"MQTT Unexpected disconnection, will try to reconnect")
            self.reconnect()
            
    def reconnect(self):
        attempts = 0
        while not self.client.is_connected() and attempts < self.max_reconnect_attempts:
            try:
                print(f"Attempting to reconnect to MQTT broker ({attempts+1}/{self.max_reconnect_attempts})...")
                self.client.reconnect()
                return True
            except Exception as e:
                print(f"Reconnection attempt failed: {e}")
                time.sleep(self.reconnect_delay)
                attempts += 1
        
        if not self.client.is_connected():
            print("Failed to reconnect to MQTT broker after multiple attempts")
            return False
            
        return True
        
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        
        print(f"MQTT Message received: {topic} - {payload}")
        
        if topic in self.topic_callbacks:
            for callback in self.topic_callbacks[topic]:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"Error in callback for topic {topic}: {e}")
                    
    def start(self):
        if self.running:
            return
            
        try:
            self.client.connect(self.broker, self.port, 60)
            self.running = True
            
            self.thread = threading.Thread(target=self.client.loop_forever)
            self.thread.daemon = True
            self.thread.start()
            print(f"MQTT client started, connected to {self.broker}:{self.port}")
            
            self.publish_game_status("READY")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            
    def stop(self):
        if not self.running:
            return
        
        try:
            self.publish_game_status("STOPPED")
        except:
            pass
            
        self.client.disconnect()
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def publish(self, topic, message):
        if not self.running:
            print("MQTT client not running")
            return False
            
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
                
            result = self.client.publish(topic, message)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Failed to publish message to {topic}, result code: {result.rc}")
                return False
                
            return True
        except Exception as e:
            print(f"Failed to publish MQTT message: {e}")
            return False
            
    def subscribe(self, topic, callback=None):
        if topic not in self.subscribed_topics:
            self.subscribed_topics.append(topic)
            
        if not self.running:
            print(f"MQTT client not running, topic {topic} will be subscribed at connection")
            if callback:
                if topic not in self.topic_callbacks:
                    self.topic_callbacks[topic] = []
                self.topic_callbacks[topic].append(callback)
            return True
            
        try:
            if callback:
                if topic not in self.topic_callbacks:
                    self.topic_callbacks[topic] = []
                self.topic_callbacks[topic].append(callback)
                
            result, _ = self.client.subscribe(topic)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"Successfully subscribed to {topic}")
                return True
            else:
                print(f"Failed to subscribe to {topic}, result code: {result}")
                return False
                
        except Exception as e:
            print(f"Failed to subscribe to MQTT topic: {e}")
            return False
    
    def update_ball_position(self, ball_shape):
        current_time = time.time() * 1000
        
        if current_time - self.last_position_update_time < self.ball_position_update_interval:
            return False
            
        self.last_position_update_time = current_time
        
        if ball_shape and hasattr(ball_shape, 'body'):
            position = ball_shape.body.position
            velocity = ball_shape.body.velocity
            
            position_changed = (abs(position.x - self.last_ball_position["x"]) > 1 or 
                               abs(position.y - self.last_ball_position["y"]) > 1)
            velocity_changed = (abs(velocity.x - self.last_ball_position["vx"]) > 5 or 
                               abs(velocity.y - self.last_ball_position["vy"]) > 5)
                               
            if position_changed or velocity_changed:
                self.last_ball_position = {
                    "x": position.x,
                    "y": position.y,
                    "vx": velocity.x,
                    "vy": velocity.y
                }
                return self.publish_ball_position(position.x, position.y, velocity.x, velocity.y)
                
        return False
            
    def publish_ball_position(self, x, y, velocity_x, velocity_y):
        data = {
            "x": x,
            "y": y,
            "vx": velocity_x,
            "vy": velocity_y,
            "timestamp": time.time()
        }
        return self.publish(BALL_POSITION_TOPIC, data)
        
    def publish_score_update(self, points):
        return self.publish(SCORE_TOPIC, str(points))
        
    def publish_bumper_hit(self, bumper_id, points):
        data = {
            "id": bumper_id,
            "points": points,
            "timestamp": time.time()
        }
        return self.publish(BUMPER_HIT_TOPIC, data)
        
    def publish_game_status(self, status, value=None):
        data = {
            "status": status,
            "value": value,
            "timestamp": time.time()
        }
        return self.publish(GAME_STATUS_TOPIC, data)