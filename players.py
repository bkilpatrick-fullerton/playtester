from dataclasses import dataclass
import game_engine 
import random
from enum import Enum


@dataclass
class RandomPlayer:
    name: str = "RandomPlayer"
    # draw_type: str = "random" # random|deck
    # play_type: str = "random" # random|lowest

    def select_action(self, game_instance: game_engine.GameInstance) -> dict:
        phase = game_instance.phase
        actions = game_instance.get_legal_actions()
        #print(f"<<debug: {self.name}'s Turn: phase: {phase}, player_type: {self.draw_type if phase == "draw" else self.play_type}")
        # print(f"<< LEGAL ACTIONS >>")
        # print(actions)

        return random.choice(actions)

    
@dataclass
class DumbPlayer:
    name: str = "DumbPlayer"

    def select_action(self, game_instance: game_engine.GameInstance) -> dict:
        phase = game_instance.phase
        actions = game_instance.get_legal_actions()
        #print(f"<<debug: {self.name}'s Turn: phase: {phase}, player_type: {self.draw_type if phase == "draw" else self.play_type}")
        #print(f"<< LEGAL ACTIONS >>\n{actions}")

        # draw phase
        if phase == "draw":
            selected_action = {"type": "draw_deck"}

        # play phase
        if phase == "play":
            selected_action = None
            for action in actions:
                # if lowest_play_action is None, set it to the first action
                if selected_action is None:
                    #print(f"<<debug: initializing selected action: {action} >>")
                    selected_action = action
                    continue

                # otherwise, look for the lowest play action
                is_this_play_action = action["type"] == "play_playpile"
                this_value = action["card"].value
                current_selected_value = selected_action["card"].value

                if is_this_play_action and this_value < current_selected_value:
                    selected_action = action

        # submit action
        return selected_action
