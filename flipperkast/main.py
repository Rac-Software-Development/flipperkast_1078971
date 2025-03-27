from game.game_manager import GameManager
from game.score_panel import ScorePanel
from ui.display import Display

if __name__ == "__main__":
    scorepanel = ScorePanel() 
    game = GameManager()
    display = Display(game.ball, game.bumpers)
    display.run()
    scorepanel.mqtt.stop() 
