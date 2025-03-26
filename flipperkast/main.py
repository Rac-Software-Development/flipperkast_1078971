from game.game_manager import GameManager
from game.score_panel import ScorePanel

if __name__ == "__main__":
    scorepanel = ScorePanel() 
    game = GameManager()
    game.run()
    scorepanel.mqtt.stop() 
