import random

from notty.element_action.card import Deck
from notty.element_action.player import Player, AIPlayer, EasyAIPlayer

"----------------------------------------Game Engine Setting----------------------------------------"
class GameEngine:
    def __init__(self, num_ai=1, ai_difficulty="hard"):
        # player information
        self.num_ai = num_ai  # Default = 1 AI opponent
        self.ai_difficulty = ai_difficulty  # "easy" or "hard"
        self.players = [Player("You", is_human=True)]  # First player is human

        # Create AI based on difficulty
        for i in range(num_ai):
            if ai_difficulty == "easy":
                self.players.append(EasyAIPlayer(f"NPC {i + 1}"))
            else:
                self.players.append(AIPlayer(f"NPC {i + 1}"))

        # Setup deck
        self.deck = Deck()
        self.deck.shuffle()
        self.discard_pile = []

        # Flags for in-turn actions
        self.used_draw = 0
        self.used_steal = False
        self.used_draw_discard = False
        self.turn_ended = False

        # NEW: Player drew 1 card and must discard one before ending turn
        self.pending_discard_required = False

        # Game state
        self.round = 1
        self.current_index = 0  # Current player index (0 = human)
        self.current_player = self.players[self.current_index].name
        self.winner = None

        # Initial dealing
        self._deal_initial_cards()

        # Last AI action record (for UI)
        self.last_ai_log = None

        # Optional: AI delay processing for UI animation
        self.ai_wait_until = None
        self.pending_ai_logs = []
        self.ai_wait_until = None

    "----------------------------------------Reset turn action flags----------------------------------------"
    def reset_turn_flags(self):
        self.used_draw = 0
        self.used_steal = False
        self.used_draw_discard = False
        self.turn_ended = False
        self.pending_discard_required = False

    "----------------------------------------Cards dealt at the start----------------------------------------"
    def _deal_initial_cards(self):
        for player in self.players:
            cards = self.deck.draw(4)
            player.receive_cards(cards)
        # Reset flags only after all players receive opening cards
        self.reset_turn_flags()

    "----------------------------------------Move to next player----------------------------------------"
    def next_player(self):
        # Move to the next player automatically
        self.current_index = self.next_player_index(self.current_index)
        self.current_player = self.players[self.current_index].name

    "-----------------------------------------Check win condition-----------------------------------------"
    def _check_winner_after_move(self):
        for p in self.players:
            if len(p.hand) == 0:
                self.winner = p.name
                return p.name
        return None

    "-----------------------------------------Restart new game-----------------------------------------"
    def reset_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.discard_pile = []
        self.round = 1

        self.current_index = 0
        self.current_player = self.players[self.current_index].name
        self.winner = None

        for p in self.players:
            p.hand = []

        self._deal_initial_cards()
        self.last_ai_log = None

    "-------------------------------------Get next player index looped-----------------------------------------"
    def next_player_index(self, current_index):
        return (current_index + 1) % len(self.players)

    "-----------------------------------------Remaining cards in deck-----------------------------------------"
    def deck_count(self):
        return len(self.deck.cards)

    "-----------------------------------------Status bar info-----------------------------------------"
    def get_snapshot(self):
        return {
            "round": self.round,
            "current_player": self.current_player,
            "deck_count": self.deck_count(),
            "winner": self.winner
        }

    "----------------------------------Snapshot for UI rendering-----------------------------------------"
    def ui_snapshot(self):
        snapshot = {}
        snapshot["player_hand"] = self.players[0].hand
        snapshot["ai_hands"] = [p.hand for p in self.players[1:]]
        snapshot["deck_cards"] = self.deck.cards
        snapshot["discard_pile"] = self.discard_pile
        snapshot["num_ai"] = self.num_ai
        snapshot["current_player"] = self.current_player
        snapshot["winner"] = self.winner
        return snapshot

    "----------------------Recycle discard pile back into deck (shuffle)-----------------------------------------"
    def recycle_discard_pile(self):
        if not self.discard_pile:
            return 0

        moved = len(self.discard_pile)
        self.deck.cards.extend(self.discard_pile)
        random.shuffle(self.deck.cards)
        self.discard_pile.clear()
        return moved

    "----------------------------------------Player Action----------------------------------------"
    "-------------------------------------Player draws 1–3 cards----------------------------------------"
    def player_draw_up_to_three(self):
        player = self.players[0]

        # Limit: up to 3 draws
        if self.used_draw >= 3:
            return {
                "ok": False,
                "reason": "already_used",
                "message": "You already used draw-up-to-three 3 times this turn."
            }

        # Cannot draw if hand is full
        if player.is_hand_full():
            return {
                "ok": False,
                "reason": "hand_full",
                "message": "Your hand is full (20 cards)."
            }

        # Cannot draw if deck empty
        if len(self.deck.cards) == 0:
            return {
                "ok": False,
                "reason": "deck_empty",
                "message": "Deck is empty."
            }

        # Draw 1 card
        drawn_cards = player.draw(self.deck, 1)   # always returns list

        if not drawn_cards:
            return {
                "ok": False,
                "reason": "draw_failed",
                "message": "Could not draw a card."
            }

        self.used_draw += 1

        return {
            "ok": True,
            "drawn": drawn_cards,
            "message": f"You drew 1 card ({self.used_draw}/3 this turn)."
        }

    "--------------------(first step of draw-one-discard-one)----------------------------------------"
    #Player draws 1 card
    def player_draw_one_for_discard(self):
        player = self.players[0]

        # Already drew and waiting to discard
        if self.pending_discard_required:
            return {
                "ok": False,
                "reason": "already_drawn_waiting_discard",
                "message": "You have already drawn 1 card. Please discard 1 card first."
            }

        # The draw-discard action already completed this turn
        if self.used_draw_discard:
            return {
                "ok": False,
                "reason": "draw_discard_used",
                "message": "You have already used draw-and-discard this turn."
            }

        # Hand full
        if player.is_hand_full():
            return {
                "ok": False,
                "reason": "hand_full",
                "message": "Your hand is already full (20 cards)."
            }

        # Deck empty
        if len(self.deck.cards) == 0:
            return {
                "ok": False,
                "reason": "deck_empty",
                "message": "Deck is empty, cannot draw."
            }

        # Draw one card
        drawn_cards = player.draw(self.deck, 1)  # Return list
        if not drawn_cards:
            return {
                "ok": False,
                "reason": "draw_failed",
                "message": "Could not draw a card."
            }

        # Mark that a discard is now required
        self.pending_discard_required = True

        return {
            "ok": True,
            "drawn": drawn_cards,
            "message": "You drew 1 card. Please choose 1 card to discard."
        }

    "--------------------(second step of draw-one-discard-one)---------------------------------------"
    #Player discards one card
    def player_discard_one_after_draw(self, discard_index):
        player = self.players[0]

        # Must draw first before discarding
        if not self.pending_discard_required:
            return {
                "ok": False,
                "reason": "no_pending_discard",
                "message": "You must draw 1 card for draw-and-discard before discarding."
            }

        # Index validation
        if discard_index < 0 or discard_index >= len(player.hand):
            return {
                "ok": False,
                "reason": "invalid_discard_index",
                "message": "Invalid card index."
            }

        # Remove selected card
        discarded = player.remove_card_at_index(discard_index)
        if discarded is None:
            return {
                "ok": False,
                "reason": "remove_failed",
                "message": "Failed to discard the selected card."
            }

        # Add to discard pile
        self.discard_pile.append(discarded)

        # Completed draw-and-discard
        self.pending_discard_required = False
        self.used_draw_discard = True

        # Check win condition
        self._check_winner_after_move()

        return {
            "ok": True,
            "discarded": discarded,
            "message": "You discarded 1 card to complete draw-and-discard."
        }

    "-------------------------Player steals a card---------------------------------------"
    def player_steal(self, target_index):

        if self.used_steal:
            return {
                "ok": False,
                "reason": "already_used",
                "message": "You already used the steal action this turn."
            }

        player = self.players[0]

        if target_index < 1 or target_index >= len(self.players):
            return {
                "ok": False,
                "reason": "invalid_target",
                "message": "Invalid target player index."
            }

        target = self.players[target_index]
        stolen = player.take_random_card(target)
        self.used_steal = True

        if stolen is None:
            return {
                "ok": False,
                "reason": "failed",
                "message": "Could not steal a card (target empty or your hand is full)."
            }

        # Check win condition
        self._check_winner_after_move()

        return {
            "ok": True,
            "stolen": stolen,
            "target": target.name,
            "message": f"You stole a card from {target.name}."
        }

    "-------------------------Group Detection---------------------------------------"

    def _is_sequence_group(self, cards):
    #Check if cards form a valid sequence group: 3+ cards, same suit/colour, and numbers consecutive.
        if len(cards) < 3:
            return False

        colours = [c.colour for c in cards]
        numbers = sorted(c.number for c in cards)

        # Must be same colour/suit
        if len(set(colours)) != 1:
            return False

        # Must be consecutive numbers
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] != 1:
                return False

        return True

    def _is_same_rank_diff_suit_group(self, cards):
    #Check if cards form a valid same-rank group: 4+ cards, same rank, all suits/colours different
        if len(cards) < 4:
            return False

        numbers = [c.number for c in cards]
        colours = [c.colour for c in cards]

        if len(set(numbers)) != 1:
            return False

        if len(set(colours)) != len(colours):
            return False

        return True

    def player_discard_group(self, card_group):
    # Player discards a group of cards if they form a valid combination
        player = self.players[0]
        # Every card must exist in hand
        for c in card_group:
            if c not in player.hand:
                return {
                    "ok": False,
                    "reason": "card_not_in_hand",
                    "message": "Some cards in the group are not in your hand."
                }

        is_sequence = self._is_sequence_group(card_group)
        is_same_rank = self._is_same_rank_diff_suit_group(card_group)

        # Must match one of the valid group patterns
        if not (is_sequence or is_same_rank):
            return {
                "ok": False,
                "reason": "invalid_group",
                "message": "Group must either consist of at least three consecutive cards of the same suit, or at least four cards of the same rank with all suits different."
            }

        # Remove cards from hand and add to discard pile
        player.remove_cards(card_group)
        self.discard_pile.extend(card_group)

        # Check win instantly if hand becomes empty
        if player.has_empty_hand():
            self.winner = player.name

        # Check global win state
        self._check_winner_after_move()

        return {
            "ok": True,
            "discarded_group": card_group,
            "message": "You discarded a valid group."
        }

    "-------------------------AI Group Detection---------------------------------------"

    def ai_take_turn(self, ai_index):
        ai = self.players[ai_index]

        # Basic Filters
        if ai.is_human:
            return None

        # There is already a winner → AI cannot continue
        if self.winner is not None:
            return None

        # If AI has no cards → immediate win
        if ai.has_empty_hand():
            self.winner = ai.name
            return {"name": ai.name, "action": "pass", "result": "win"}

        others = [p for i, p in enumerate(self.players) if i != ai_index]

        # AI Decision
        decision = ai.think_action(self.deck, others)
        action = decision.get("action")
        log = {"name": ai.name, "action": action}

        # DISCARD GROUP (play a valid card combination)
        if action == "discard_group":
            group = decision.get("group", [])

            valid = (len(group) >= 3 and all(c in ai.hand for c in group))
            if valid:
                ai.remove_cards(group)
                self.discard_pile.extend(group)
                log["result"] = "ok"
                log["discarded_group"] = group
            else:
                log["result"] = "invalid_group"

            # Win condition check
            if ai.has_empty_hand():
                self.winner = ai.name
                log["win"] = True
                return log

            log["win"] = False
            return log

        # STEAL
        if action == "steal":
            target = decision.get("target")

            if not target or target.hand_size() == 0:
                log["result"] = "fail"
            else:
                stolen = ai.take_random_card(target)
                if stolen:
                    log.update({
                        "result": "ok",
                        "stolen": stolen,
                        "target": target.name
                    })
                else:
                    log["result"] = "fail"

            if ai.has_empty_hand():
                self.winner = ai.name
                log["win"] = True
                return log

            log["win"] = False
            return log

        # PASS
        if action == "pass":
            log["result"] = "pass"

            if ai.has_empty_hand():
                self.winner = ai.name
                log["win"] = True
            else:
                log["win"] = False

            return log

        # DRAW_MULTIPLE
        if action == "draw_multiple":

            log["action"] = "draw_multiple"
            log["player"] = ai.name

            # Cannot draw
            if ai.is_hand_full() or not self.deck.cards:
                log["result"] = "fail"
                log["drawn"] = []
                log["message"] = f"{ai.name} wanted to draw multiple cards but could not."
                log["win"] = False
                return log

            # Success
            drawn = ai.draw_multiple(self.deck)

            log["result"] = "ok"
            log["drawn"] = drawn
            log["message"] = f"{ai.name} drew {len(drawn)} cards."
            log["win"] = False
            return log

        # DRAW & DISCARD
        if action == "draw_and_discard":

            if ai.is_hand_full() or not self.deck.cards:
                log["result"] = "fail"
                log["win"] = False
                return log

            drawn, discarded = ai.draw_and_discard(self.deck, others)
            log["drawn"] = drawn
            log["discarded"] = discarded

            if discarded is not None:
                self.discard_pile.append(discarded)

            if ai.has_empty_hand():
                self.winner = ai.name
                log["result"] = "ok"
                log["win"] = True
                return log

            log["result"] = "ok"
            log["win"] = False
            return log

        # DRAW
        if action == "draw":

            if ai.is_hand_full() or not self.deck.cards:
                log["result"] = "fail"
                log["win"] = False
                return log

            drawn_cards = ai.draw(self.deck, 1)
            log["drawn"] = drawn_cards or []

            if drawn_cards:
                log["result"] = "ok"
            else:
                log["result"] = "fail"

            if ai.has_empty_hand():
                self.winner = ai.name
                log["win"] = True
            else:
                log["win"] = False

            return log

        # Unknown Action
        log["result"] = "unknown_action"
        log["win"] = False
        return log

    "-------------------------AI players take action---------------------------------------"
    # Let all AI players take action once in sequence
    def run_ai_phase(self):

        logs = []

        for ai_index in range(1, len(self.players)):
            if self.winner is not None:
                break

            log = self.ai_take_turn(ai_index)
            if log is not None:
                logs.append(log)

        self.pending_ai_logs = logs
        return logs

    "-------------------------AI players end action---------------------------------------"
    def end_player_turn(self):
        if self.winner is not None:
            return {
                "ok": False,
                "reason": "game_over",
                "message": f"Game already finished. Winner: {self.winner}"
            }

        # Must complete discard if player used draw-and-discard and hasn't discarded yet
        if self.pending_discard_required:
            return {
                "ok": False,
                "reason": "pending_discard",
                "message": "You must discard 1 card to finish the draw-and-discard action before ending your turn."
            }

        self.turn_ended = True

        # Move to next player
        self.next_player()

        # When player turn ends → reset all available actions for next turn
        self.reset_turn_flags()

        return {
            "ok": True,
            "winner": None,
            "message": "Player ended turn. NPC phase will run step by step."
        }

    "-------------------------Formating AI message---------------------------------------"

    def _format_ai_message(self, log):
        name = log.get("name", "NPC")
        action = log.get("action")

        # Discard group
        if action == "discard_group":
            group = log.get("discarded_group", [])
            return f"{name} discarded a valid group of {len(group)} cards."

        # Steal
        if action == "steal":
            target = log.get("target")
            if log.get("result") == "ok":
                return f"{name} stole a card from {target}."
            return f"{name} tried to steal a card but failed."

        # Draw Multiple
        if action == "draw_multiple":
            drawn = log.get("drawn", [])
            n = len(drawn)
            if log.get("result") != "ok":
                return f"{name} tried to draw multiple cards but failed."
            return f"{name} drew {n} cards."

        # Draw & Discard
        if action == "draw_and_discard":
            drawn = log.get("drawn", [])
            n = len(drawn) if drawn else 0
            if log.get("result") != "ok":
                return f"{name} tried to draw and discard but failed."
            if n == 0:
                return f"{name} discarded 1 card."
            elif n == 1:
                return f"{name} drew 1 card and discarded 1 card."
            else:
                return f"{name} drew {n} cards and discarded 1 card."

        # Draw only
        if action == "draw":
            drawn = log.get("drawn", [])
            n = len(drawn)
            if log.get("result") != "ok":
                return f"{name} tried to draw a card but failed."
            return f"{name} drew {n} card." if n == 1 else f"{name} drew {n} cards."

        # Pass
        if action == "pass":
            return f"{name} chose to pass this turn."

        return f"{name} performed an action."

    "-------------------------AI turn System---------------------------------------"
    def run_single_ai_turn(self):

        # If a winner already exists, stop execution
        if self.winner is not None:
            return True, {"message": f"Game over. Winner: {self.winner}"}

        # Safety: AI should not act during the human player's turn
        if self.current_index == 0:
            self.next_player()

        ai_index = self.current_index
        log = self.ai_take_turn(ai_index)

        # If AI wins → stop immediately, do not switch players
        if self.winner is not None:
            return True, log

        # Format readable AI message
        if log:
            log["message"] = self._format_ai_message(log)

        # If discarding cards → UI should pick up discarded pile
        if log and ("discarded" in log or "discarded_group" in log):
            log["needs_recycle"] = True

        # Move to next player
        self.next_player()

        # If turn returns to human player → AI phase ends
        if self.current_index == 0:
            self.round += 1
            self.reset_turn_flags()
            return True, log

        # Continue to next NPC
        return False, log

    "-------------------------Auto-play assistant for human player (uses AI logic)---------------------------------------"

    def player_draw_and_discard(self, discard_index):

        # Draw 1 card
        result_draw = self.player_draw_one_for_discard()

        if not result_draw.get("ok"):
            return {
                "ok": False,
                "message": "AI failed to draw a card."
            }

        # Discard the chosen index
        result_discard = self.player_discard_one_after_draw(discard_index)

        if not result_discard.get("ok"):
            return {
                "ok": False,
                "message": "AI could not discard the selected card."
            }

        return {
            "ok": True,
            "action": "draw_and_discard",
            "drawn": result_draw.get("drawn"),
            "discarded": result_discard.get("discarded"),
            "message": "AI completed draw and discard."
        }

    def player_auto_play(self):

        human = self.players[0]
        other_players = self.players[1:]

        # Duplicate user's cards
        ai_brain = AIPlayer("temp")
        ai_brain.hand = human.hand[:]

        decision = ai_brain.think_action(self.deck, other_players)
        action = decision["action"]
        log = []

        # Discard_group
        if action == "discard_group":
            group = decision["group"]
            result = self.player_discard_group(group)
            log.append(result)
            return {
                "ok": True, "log": log,
                "message": "AI helped you discard a group."
            }

        # Steal
        if action == "steal":
            target = decision["target"]
            target_index = self.players.index(target)
            result = self.player_steal(target_index)
            log.append(result)
            return {
                "ok": True, "log": log,
                "message": f"AI helped you steal from {target.name}."
            }

        # Draw_multiple
        if action == "draw_multiple":
            drawn = human.draw(self.deck, 3)
            log.append({"drawn": drawn, "action": "draw_multiple"})
            return {
                "ok": True, "log": log,
                "message": "AI helped you draw multiple cards."
            }

        # Draw
        if action == "draw":
            drawn = human.draw(self.deck, 1)
            log.append({"drawn": drawn, "action": "draw"})
            return {
                "ok": True, "log": log,
                "message": "AI helped you draw a card."
            }

        # draw_and_discard
        if action == "draw_and_discard":
            idx = ai_brain.choose_discard_index(other_players)
            result = self.player_draw_and_discard(idx)
            log.append(result)
            return {
                "ok": True, "log": log,
                "message": "AI helped you draw and discard."
            }

        # pass
        if action == "pass":
            log.append({"action": "pass", "player": "You"})
            return {
                "ok": True, "log": log,
                "message": "AI thinks you should pass."
            }

        # Unknow
        return {"ok": False, "message": f"Unknown AI action: {action}"}

    "-------------------------difficulty setting-------------------------------------"
    def set_difficulty(self, difficulty):
        #Update AI difficulty and rebuild all AI players
        self.ai_difficulty = difficulty

        # Rebuild player list (keep human)
        human = self.players[0]
        new_players = [human]

        # Recreate all AI players
        for i in range(self.num_ai):
            if difficulty == "easy":
                new_players.append(EasyAIPlayer(f"NPC {i+1}"))
            else:
                new_players.append(AIPlayer(f"NPC {i+1}"))

        self.players = new_players

        # Restart game session
        self.reset_game()

"-------------------------Referencing-------------------------------------"
# GeeksforGeeks — War Card Game in Python: simple OOP card game example with deck shuffle/draw logic
# https://www.geeksforgeeks.org/python/war-card-game-in-python/

# Deckbuilder(GitHub project for deck‑building / card‑game management)
# https://github.com/pwildenhain/terminal_playing_cards/tree/master/terminal_playing_cards
# deck management,discard/reshuffle logic,card draw/deal/discard—conceptually - discard_pile, deck, and recycling logic.

# Arcade’s Solitaire tutorial — for deck/shuffle/draw/deal mechanics and basic game structure.
# https://api.arcade.academy/en/2.6.0/tutorials/card_game/



