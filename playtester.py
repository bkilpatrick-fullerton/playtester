from dataclasses import dataclass, field
import random
from datetime import datetime
from game_engine import GameInstance, GameSettings, Card, Location
from players import DumbPlayer, RandomPlayer
from pathlib import Path

TEMP_DIR = Path(__file__).parent / "temp_files"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def run_game(game_id: str = None, game_settings: GameSettings = None, player_1: object = None, player_2: object = None):
    # initialize game
    game_id = game_id or f"game_{game_settings.get_setting_code()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    game_settings = game_settings or GameSettings() # default settings
    game_instance = GameInstance(game_id=game_id, settings=game_settings)

    # initialize players
    player_1 = player_1 or DumbPlayer()
    player_2 = player_2 or RandomPlayer()
    
    # create log file path
    log_file_path = TEMP_DIR / f"{game_id}_game_log.txt"
    
    # play game
    # deck_size = len(game_instance.locations["deck"].cards)
    testing_turn_limit = 100
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Game ID: {game_id}\n")
        log_file.write(f"Game Settings: {game_settings}\n")
        log_file.write(f"Player 1: {player_1.name}\n")
        log_file.write(f"Player 2: {player_2.name}\n")
        log_file.write("=" * 50 + "\n\n")
        
        while not game_instance.get_is_game_over() and game_instance.turn < testing_turn_limit:
            game_state_string = game_instance.get_game_state_string()
            
            if game_instance.active_player == 1:
                selected_action = player_1.select_action(game_instance)
            else:
                selected_action = player_2.select_action(game_instance)

            game_state_string += f"<< SELECTED ACTION >>\n{selected_action}\n"
            #print(game_state_string)
            log_file.write(game_state_string + "\n")
            game_instance.submit_action(selected_action)

        final_game_state_string = f"<< FINAL GAME STATE >>\n{game_instance.get_game_state_string()}"
        print(final_game_state_string)
        log_file.write(final_game_state_string + "\n")
    
    print(f"Game log saved to: {log_file_path}")
    

def main():
    default_settings = GameSettings()
    run_game(game_settings=default_settings) # default settings
    run_game(game_settings=GameSettings(number_of_suits=default_settings.number_of_suits-1)) # 4 suits
    run_game(game_settings=GameSettings(number_of_suits=default_settings.number_of_suits+1)) # 6 suits
    run_game(game_settings=GameSettings(hand_size=default_settings.hand_size-1)) # 7 cards per hand
    run_game(game_settings=GameSettings(hand_size=default_settings.hand_size+1)) # 9 cards per hand
    run_game(game_settings=GameSettings(max_card_value=default_settings.max_card_value-1)) # max card value 19
    run_game(game_settings=GameSettings(max_card_value=default_settings.max_card_value+1)) # max card value 21
    run_game(game_settings=GameSettings(number_handshake_cards=default_settings.number_handshake_cards-1)) # 2 handshake cards
    run_game(game_settings=GameSettings(number_handshake_cards=default_settings.number_handshake_cards+1)) # 4 handshake cards
    
if __name__ == "__main__":
    main()