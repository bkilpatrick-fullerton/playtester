from dataclasses import dataclass, field
import random

@dataclass
class GameSettings:
    name: str = 'default'
    max_card_value: int = 10
    number_handshake_cards: int = 3
    number_of_suits: int = 5
    hand_size: int = 8

    def get_setting_code(self) -> str:
        return f"hs{self.hand_size}_ns{self.number_of_suits}_mcv{self.max_card_value}_nhc{self.number_handshake_cards}"
    
@dataclass
class Card:
    key: str
    suit: str
    value: int
    #is_seen: bool = False

@dataclass
class Location:
    name: str
    cards: list[Card] = field(default_factory=list)
    
    def add(self, card: Card) -> None:
        """Add a card to the rightmost position (end of the cards list)."""
        self.cards.append(card)
    
    def draw(self) -> Card:
        """Pop and return the rightmost card (last card in the cards list)."""
        if not self.cards:
            raise IndexError("Cannot draw from empty location")
        return self.cards.pop()

    def extract(self, card_key: str) -> Card:
        """Extract a card from the location."""
        for card in self.cards:
            if card.key == card_key:
                self.cards.remove(card)
                return card
        raise IndexError(f"Card {card_key} not found in location")

    def get_top_card(self) -> Card:
        """Get the top card from the location. READ ONLY."""
        if not self.cards:
            return None
        return self.cards[-1]

    def get_cards_as_string(self, show_label: bool = True, compact: bool = True):
        label = f"{self.name}: " if show_label else ""

        if compact:
            return f"{label}{', '.join([card.key for card in self.cards]) if self.cards else '-'} "
        else:
            return f"{label}{', '.join([str(card) for card in self.cards]) if self.cards else '-'} "

#===============================================
# Helper Functions
#===============================================
def get_card_key(suit: int, value: int, handshake_num: int = None) -> str:
    key = f"s{str(suit).zfill(2)}-v{str(value).zfill(2)}"
    if handshake_num:
        key = f'{key}-h{handshake_num}'
    return key

def get_location_key(location_type: str, suit: int = None, player: int = None) -> str:
    if location_type == "play" and suit >= 0 and player >= 1:
        key = f"play_s{str(suit).zfill(2)}_p{player}"
    elif location_type == "discard" and suit >= 0:
        key = f"discard_s{str(suit).zfill(2)}"
    elif location_type == "hand" and player >= 1:
        key = f"hand_p{player}"
    elif location_type == "deck":
        key = "deck"
    else:
        raise ValueError(f"Invalid location type: {location_type}")
    return key

def generate_cards(game_settings: GameSettings) -> list[Card]:
    """Generate all cards for the game based on the settings."""
    cards = []
    
    # card is made up of a value and a suit
    for suit in range(game_settings.number_of_suits):
        for value in range(1, game_settings.max_card_value + 1):
            # handshake cards are 0 value (will be treated as special) and there are multiple of them
            if value == 1:
                for i in range(game_settings.number_handshake_cards):
                    card = Card(key=get_card_key(suit=suit, value=0, handshake_num=i+1), suit=suit, value=0)
                    cards.append(card)
            # regular cards are treated as normal. there is only one of each
            else:
                card = Card(key=get_card_key(suit=suit, value=value), suit=suit, value=value)
                cards.append(card)
    return cards

def shuffle(cards: list[Card]) -> list[Card]:
        """Shuffle a list of cards"""
        for i in range(len(cards) - 1, 0, -1):
            j = random.randint(0, i)
            cards[i], cards[j] = cards[j], cards[i]

#===============================================
# Game Instance
#===============================================
@dataclass
class GameInstance:
    game_id: str  
    settings: GameSettings = field(default_factory=GameSettings)
    #suits: list[str] = field(default_factory=list)
    locations: dict[str,Location] = field(default_factory=dict)
    cards: set[Card] = field(default_factory=set)
    turn: int = 1
    active_player: int = 1
    phase: str = "play"
    
    def __post_init__(self):
        # generate and shuffle cards to create the deck
        cards = generate_cards(self.settings)
        random.shuffle(cards)
        location_key = get_location_key(location_type="deck")
        self.locations[location_key] = Location(name=location_key, cards=cards)
    
        # create hands for each player
        num_players = 2
        for player in range(1, num_players + 1):

            # create emptyhand for each player
            location_key = get_location_key(location_type="hand", player=player)
            self.locations[location_key] = Location(name=location_key)

            # draw cards for each player
            for i in range(self.settings.hand_size):
                self.locations[location_key].add(self.locations["deck"].draw())

            # create empty play piles for each suit for each player
            for suit in range(self.settings.number_of_suits):
                location_key = get_location_key(location_type="play", suit=suit, player=player)
                self.locations[location_key] = Location(name=location_key)

        # create a shared discard location (empty) for each suit. 
        for suit in range(self.settings.number_of_suits):
            # one discard pile per suit
            location_key = get_location_key(location_type="discard", suit=suit)
            self.locations[location_key] = Location(name=location_key)

    def get_game_info_string(self):
        return f"Turn: {self.turn}, Phase: {self.phase}, Active Player: {self.active_player}, Deck Size: {self.get_deck_size()}"
    
    def get_game_state_string(self):
        # for DEBUGGING
        game_info_string = f"<<-- GAME STATE -->>" + "\n"
        game_info_string += self.get_game_info_string() + "\n"
        game_info_string += f"<<-- HANDS -->>" + "\n"
        game_info_string += self.locations[get_location_key(location_type='hand', player=1)].get_cards_as_string() + "\n"
        game_info_string += self.locations[get_location_key(location_type='hand', player=2)].get_cards_as_string() + "\n"
        game_info_string += f"<<-- PLAY PILES -->>" + "\n"
        for suit in range(self.settings.number_of_suits):
            print_str = f"s{str(suit).zfill(2)} " 
            print_str += f"({self.locations[get_location_key(location_type='play', suit=suit, player=1)].get_cards_as_string()}) "
            print_str += f"({self.locations[get_location_key(location_type='play', suit=suit, player=2)].get_cards_as_string()}) "
            print_str += f"({self.locations[get_location_key(location_type='discard', suit=suit)].get_cards_as_string()})"
            game_info_string += print_str + "\n"

        game_info_string += f"<<-- LEGAL ACTIONS -->>" + "\n"
        game_info_string += f"{self.get_legal_actions()}" + "\n"
        return game_info_string


    def print_cards_locations(self, compact: bool = True):
        # for DEBUGGING
        for name, location in self.locations.items():
            print(f"<<-- LOCATION: {name} - {len(location.cards)} cards -->>")
            location.print_cards(compact=compact)
            print(f"<<-- -->>")

    def get_deck_size(self) -> int:
        return len(self.locations["deck"].cards)

    def get_is_game_over(self) -> bool:
        return self.get_deck_size() == 0

    def advance_phase(self) -> None:
        """Advance to the next phase (which might include changing the active player)"""
        # PHASE 1: PLAY completed advance to PHASE 2: DRAW
        if self.phase == "play":
            self.phase = "draw"
            return
        # PHASE 2: DRAW completed, change active player and reset to PHASE 1: PLAY
        if self.phase == "draw":
            self.active_player = 2 if self.active_player == 1 else 1
            self.phase = "play"
            self.turn += 1
            return
        
    def draw_action(self, card: Card = None) -> None:
        """Draw a card from from_location and add it to the active player's hand.
            Includes both drawing from DECK and drawing from DISCARD (suit specific)
        """
        if card is None:
            from_location_key = get_location_key(location_type="deck")
        else:
            from_location_key = get_location_key(location_type="discard", suit=card.suit)

        to_location_key = get_location_key(location_type="hand", player=self.active_player)
        self.locations[to_location_key].add(
           self.locations[from_location_key].draw() #draw to_location from from_location
        )
        
    def play_action(self, card: Card) -> None:
        """Play a card from from_location and add it to to_location.
            Includes both playing to PLAY (suit specific) and playing to DISCARD (suit specific)
        """
        to_location_key = get_location_key(location_type="play", suit=card.suit, player=self.active_player)
        from_location_key = get_location_key(location_type="hand", player=self.active_player)
        self.locations[to_location_key].add(
            self.locations[from_location_key].extract(card.key) #extract card_key from from_location
        )
        
    def discard_action(self, card: Card) -> None:
        """Discard a card from from_location and add it to to_location.
            Includes both playing to PLAY (suit specific) and playing to DISCARD (suit specific)
        """
        to_location_key = get_location_key(location_type="discard", suit=card.suit)
        from_location_key = get_location_key(location_type="hand", player=self.active_player)
        self.locations[to_location_key].add(
            self.locations[from_location_key].extract(card.key) #extract card_key from from_location
        )

    def get_legal_actions(self) -> list[dict]:
        """Get all legal actions for the current player."""
        actions = []
        if self.get_is_game_over():
            return actions
        elif self.phase == "draw":
            actions.append({"type": "draw_deck"}) # draw from deck always allowed
            for suit in range(self.settings.number_of_suits):
                discard_location_key = get_location_key(location_type="discard", suit=suit)
                top_discard_card = self.locations[discard_location_key].get_top_card()
                if top_discard_card:
                    actions.append({"type": "draw_discard", "card": top_discard_card})
        elif self.phase == "play":
            hand_location_key = get_location_key(location_type="hand", player=self.active_player)
            for card in self.locations[hand_location_key].cards:
                suit = card.suit
                # its always legal to DISCARD a card
                actions.append({"type": "play_discard", "card": card})
                # check for legal PLAY locations
                play_location_key = get_location_key(location_type="play", suit=suit, player=self.active_player)
                if len(self.locations[play_location_key].cards) == 0 or self.locations[play_location_key].cards[-1].value <= card.value:
                    actions.append({"type": "play_playpile", "card": card})

        return actions

    def submit_action(self, action: dict) -> None:
        card = action.get("card", None)
        if action["type"] == "draw_deck":
            self.draw_action()
        elif action["type"] == "draw_discard":
            self.draw_action(card=card)
        elif action["type"] == "play_discard":
            self.discard_action(card=card)
        elif action["type"] == "play_playpile":
            self.play_action(card=card)
        else:
            raise ValueError(f"Invalid action type: {action['type']}")

        self.advance_phase()

       
def main():
    # TEST CODE
    game_settings = GameSettings() # default settings
    game_instance = GameInstance(game_id="1", settings=game_settings)
    #game_instance.print_game_state()

    play_turns = 4
    for play_turn in range(play_turns):
        game_instance.print_game_state()
        # get legal actions
        actions = game_instance.get_legal_actions()
        print(f"Legal Actions: {len(actions)}")
        for action in actions:
            print(action)  
        # submit random action
        selected_action = random.choice(actions)
        print(f"Submitting action: {selected_action}")
        game_instance.submit_action(selected_action)

if __name__ == "__main__":
    main()