import random
class Player:
    def __init__(self, name, is_human=False):
        """
        Initialize a Player object.

        Parameters
        ----------
        name : str
            The player's name.
        is_human : bool, optional
            Whether the player is human (default is False).

        Attributes
        ----------
        name : str
            Name of the player.
        is_human : bool
            True if the player is human; False if controlled by the computer.
        hand : list
            The player's current hand of cards.
        """
        self.name = name
        self.is_human = is_human
        self.hand = []

    def receive_cards(self, cards):
        # Add a list of cards to the player's hand
        self.hand.extend(cards)

    def hand_size(self):
        # Return the current number of cards in the player's hand
        return len(self.hand)

    def is_hand_full(self):
        # Return True if the player already holds the maximum of 20 cards
        return len(self.hand) >= 20

    def has_empty_hand(self):
        # Return True if the player's hand contains no cards
        return len(self.hand) == 0

    def add_card(self, card):
        # Attempt to add a single card if the hand is not full
        # Return True on success, False if the hand is full
        if self.is_hand_full():
            return False
        self.hand.append(card)
        return True

    # ---------------------
    # Remove by index
    # ---------------------
    def _remove_at_index(self, index):
        # Remove and return the card at the given index in the hand.
        # If the index is not an integer or is out of range, return None instead.
        if not isinstance(index, int):
            return None
        if index < 0 or index >= len(self.hand):
            return None
        return self.hand.pop(index)

    def remove_card_at_index(self, index):
        # remove and return the card at the given index
        return self._remove_at_index(index)

    def remove_card(self, card):
        # Remove a card by value (first matching occurrence)
        # Returns the removed card, or None if the card is not present
        if card in self.hand:
            idx = self.hand.index(card)
            return self._remove_at_index(idx)
        return None

    def remove_cards(self, cards):
        # Remove multiple cards using remove_card for each
        for c in cards:
            self.remove_card(c)

    # ---------------------
    # Draw n cards from deck
    # ---------------------
    def draw(self, deck, n=1):
        # Draw n cards from the deck if the hand is not full and the deck has cards
        if self.is_hand_full():
            return []

        if len(deck.cards) == 0:
            return []

        drawn = deck.draw(n)
        self.hand.extend(drawn)
        return drawn

    # ---------------------
    # Draw 1 → Discard 1
    # ---------------------
    def draw_and_discard(self, deck, discard_index):
        # Draw a single card first
        drawn_cards = self.draw(deck)
        if not drawn_cards:
            return None, None
        drawn = drawn_cards[0]

        # Attempt to discard a card at the specified index
        discarded = self.remove_card_at_index(discard_index)

        # If discard index is invalid, undo the draw
        if discarded is None:
            self.remove_card(drawn)
            deck.cards.append(drawn)
            return drawn, None

        # Return both the drawn and discarded cards
        return drawn, discarded

    # ---------------------
    # Steal 1 random card from another player
    # ---------------------
    def take_random_card(self, other_player):
        # Attempt to steal a random card from another player
        # Only works if self is not full and the other player has cards
        if self.is_hand_full():
            return None
        if not other_player.hand:
            return None

        card = random.choice(other_player.hand)  # Select random card
        other_player.hand.remove(card)           # Remove from target player
        self.hand.append(card)                   # Add to own hand
        return card

class AIPlayer(Player):

    def __init__(self, name):
        # Initialize AI player with name, non-human flag, and a turn counter
        super().__init__(name, is_human=False)
        self.turn_counter = 0

    def _card_score(self, card, other_players=None):
        colours_with_same_number = set()
        neighbours = 0

        for c in self.hand:
            if c is card:
                continue
            if c.number == card.number:
                colours_with_same_number.add(c.colour)
            if c.colour == card.colour and abs(c.number - card.number) == 1:
                neighbours += 1

        same_number = len(colours_with_same_number)
        base_score = same_number * 2 + neighbours

        # If no opponent data, return own value only
        if other_players is None:
            return base_score

        # ----- opponent danger evaluation -----
        danger = 0

        for p in other_players:
            # Same number risk: card might help them complete a set
            same_num_cards = [c for c in p.hand if c.number == card.number]
            opp_colours = {c.colour for c in same_num_cards}

            if len(opp_colours) >= 3 and card.colour not in opp_colours:
                danger += 3  # dangerous for forming a 4-colour set

            # Same colour run risk: card might extend a sequence
            same_colour_cards = [c for c in p.hand if c.colour == card.colour]
            nums = sorted({c.number for c in same_colour_cards} | {card.number})

            run_len = 1
            best_run = 1
            for i in range(1, len(nums)):
                if nums[i] == nums[i-1] + 1:
                    run_len += 1
                    best_run = max(best_run, run_len)
                elif nums[i] != nums[i-1]:
                    run_len = 1

            if best_run >= 3:
                danger += best_run - 1

        # High danger reduces score
        return base_score - danger

    def _weakest_card(self, other_players=None):
        # Return the card with the lowest score (least valuable to keep)
        if not self.hand:
            return None
        best = self.hand[0]
        best_score = self._card_score(best, other_players)
        for c in self.hand[1:]:
            s = self._card_score(c, other_players)
            if s < best_score:
                best, best_score = c, s
        return best

    def choose_discard_index(self, other_players=None):
        # Choose the index of the weakest card to discard
        weakest = self._weakest_card(other_players)
        if weakest is None:
            return 0
        return self.hand.index(weakest)

    # ---------------------
    # Detect sequences (same colour, consecutive numbers)
    # ---------------------
    def find_sequences(self):
        groups = []
        by_colour = {}

        for c in self.hand:
            by_colour.setdefault(c.colour, []).append(c)

        for colour, cards in by_colour.items():
            cards.sort(key=lambda x: x.number)
            if len(cards) < 3:
                continue

            current = [cards[0]]
            for i in range(1, len(cards)):
                prev, cur = cards[i - 1], cards[i]
                if cur.number == prev.number + 1:
                    current.append(cur)
                elif cur.number == prev.number:
                    continue
                else:
                    if len(current) >= 3:
                        groups.append(current[:])
                    current = [cur]

            if len(current) >= 3:
                groups.append(current[:])

        return groups

    # ---------------------
    # Detect sets (same number, different colours)
    # ---------------------
    def find_sets(self):
        groups = []
        by_num = {}

        for c in self.hand:
            by_num.setdefault(c.number, []).append(c)

        for num, cards in by_num.items():
            seen_colours = set()
            uniq = []

            for c in cards:
                if c.colour not in seen_colours:
                    seen_colours.add(c.colour)
                    uniq.append(c)

            if len(uniq) >= 4:
                groups.append(uniq)

        return groups

    # ---------------------
    # Evaluate threat level of another player
    # ---------------------
    def _threat_score(self, player):
        # Sequence score
        by_colour = {}
        for c in player.hand:
            by_colour.setdefault(c.colour, []).append(c)

        seq_score = 0
        for cards in by_colour.values():
            cards.sort(key=lambda x: x.number)
            run_len = 1
            for i in range(1, len(cards)):
                if cards[i].number == cards[i-1].number + 1:
                    run_len += 1
                    seq_score = max(seq_score, run_len)
                elif cards[i].number != cards[i-1].number:
                    run_len = 1

        # Set score
        by_num = {}
        for c in player.hand:
            by_num.setdefault(c.number, []).append(c)

        set_score = 0
        for cards in by_num.values():
            colours = {c.colour for c in cards}
            set_score = max(set_score, len(colours))

        return seq_score * 2 + set_score * 3 + len(player.hand) * 0.2

    def choose_steal_target(self, other_players):
        # Choose the opponent with highest threat score who has cards
        candidates = [p for p in other_players if p.hand_size() > 0]
        if not candidates:
            return None
        return max(candidates, key=self._threat_score)

    # ---------------------
    # Draw 1, then discard weakest
    # ---------------------
    def draw_and_discard(self, deck, other_players, discard_index=None):
        if self.is_hand_full():
            return [], None

        drawn = self.draw(deck, 1)
        if not drawn:
            return [], None

        idx = self.choose_discard_index(other_players)
        discarded = self.remove_card_at_index(idx)
        return drawn, discarded

    # ---------------------
    # Draw multiple cards depending on hand size (no discard)
    # ---------------------
    def draw_multiple(self, deck):
        if self.is_hand_full():
            return []

        n = self.hand_size()

        if 1 <= n <= 5:
            draw_count = 3  # build hand early
        elif 6 <= n <= 15:
            draw_count = 1
        else:
            draw_count = 1

        return self.draw(deck, draw_count)

    # ---------------------
    # Decide AI action for this turn
    # ---------------------
    def think_action(self, deck, other_players):
        self.turn_counter += 1

        # 1) If we already have valid groups, discard the biggest one
        seqs = self.find_sequences()
        sets_ = self.find_sets()
        groups = seqs + sets_
        if groups:
            best_group = max(groups, key=len)
            return {
                "action": "discard_group",
                "group": best_group
            }

        # 2) After 15 turns, simplify: draw-one-discard-one only
        if self.turn_counter > 15:
            if not self.is_hand_full() and len(deck.cards) > 0:
                return {
                    "action": "draw_and_discard",
                    "other_players": other_players
                }
            return {"action": "pass"}

        # 3) Every 8th turn, attempt to steal from most dangerous opponent
        if self.turn_counter % 8 == 0 and not self.is_hand_full():
            target = self.choose_steal_target(other_players)
            if target is not None:
                return {
                    "action": "steal",
                    "target": target
                }

        # 4) Early game: draw multiple to build hand; otherwise refine with draw/discard
        if not self.is_hand_full() and len(deck.cards) > 0:
            n = self.hand_size()
            if n <= 5:
                return {"action": "draw_multiple"}
            else:
                return {
                    "action": "draw_and_discard",
                    "other_players": other_players
                }

        # 5) Default fallback action
        return {"action": "pass"}


class EasyAIPlayer(AIPlayer):
    def __init__(self, name):
        # Initialize as an AIPlayer but with simplified behaviour
        super().__init__(name)
        # Cycle steps: 0 = pass, 1 = steal, 2 = draw, 3 = draw & discard
        self._cycle_step = 0

    # ---------------------
    # Choose random discard index
    # ---------------------
    def choose_discard_index(self, other_players=None):
        # Randomly choose a card to discard; if hand empty, return 0
        return random.randrange(len(self.hand)) if self.hand else 0

    # ---------------------
    # Choose random target to steal from
    # ---------------------
    def choose_steal_target(self, others):
        # Pick a random opponent who has cards
        candidates = [p for p in others if p.hand]
        return random.choice(candidates) if candidates else None

    # ---------------------
    # Decide AI action for this turn (simple repeating cycle)
    # ---------------------
    def think_action(self, deck, others):
        """
        EASY AI behaviour cycle:
        1) pass
        2) steal
        3) draw
        4) draw_and_discard
        Then repeat.
        """
        step = self._cycle_step % 4
        self._cycle_step += 1

        # 1. Pass
        if step == 0:
            return {"action": "pass"}

        # 2. Steal — if possible; otherwise draw
        if step == 1:
            target = self.choose_steal_target(others)
            if target is not None:
                return {"action": "steal", "target": target}
            return {"action": "draw"}

        # 3. Draw one card
        if step == 2:
            # If deck empty or hand full, pass
            if not deck.cards or self.is_hand_full():
                return {"action": "pass"}
            return {"action": "draw"}

        # 4. Draw one card and discard randomly
        if step == 3:
            # If cannot draw or cannot discard, pass
            if not deck.cards or self.is_hand_full() or not self.hand:
                return {"action": "pass"}
            return {
                "action": "draw_and_discard",
                "discard_index": self.choose_discard_index(others)
            }


# Reference
# McGugan, W. (2007). *Beginning Game Development with Python and Pygame: From Novice to Professional*. Apress.
# https://github.com/Thomas-McKanna/Uno-Python