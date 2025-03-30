from game.game_manager import GameManager
from display import Display

def main():
    game_manager = GameManager()
    
    display = Display(
        game_manager.space,
        game_manager.ball_shape,
        flippers=game_manager.get_flippers(),
        bumpers=game_manager.bumpers,
        plunger=game_manager.plunger
    )
    
    try:
        display.run(game_manager)
    finally:
        game_manager.stop()

if __name__ == "__main__":
    main()