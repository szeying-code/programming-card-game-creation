"""Headless check of the game engine (no window, no pygame needed).

Plays many full games in which the human seat is driven by the built-in auto-play helper
and the opponents are the AI players, then reports how the games ended.

Run from the main folder of the repository:
    python simulate_games.py            # 100 games per difficulty
    python simulate_games.py 500        # choose the number of games
"""
import random
import sys
from collections import Counter

from notty.element_action.game import GameEngine

MAX_TURNS = 400  # a game that lasts longer than this is counted as unfinished


def play_one(difficulty, num_ai):
    engine = GameEngine(num_ai=num_ai, ai_difficulty=difficulty)
    for turn in range(MAX_TURNS):
        if engine.winner:
            return engine.winner, turn
        # In the game window the interface moves the discard pile back into the deck and
        # reshuffles it; here we do the same whenever the deck has run out.
        if engine.deck_count() == 0:
            engine.recycle_discard_pile()
        engine.player_auto_play()
        if engine.winner:
            return engine.winner, turn
        engine.end_player_turn()
        if engine.deck_count() == 0:
            engine.recycle_discard_pile()
        engine.run_ai_phase()
    return engine.winner, MAX_TURNS


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    random.seed(2025)
    for difficulty in ("easy", "hard"):
        for num_ai in (1, 2):
            results, turns, errors = Counter(), [], 0
            for _ in range(games):
                try:
                    winner, n = play_one(difficulty, num_ai)
                except Exception as exc:  # report engine errors instead of stopping
                    errors += 1
                    last_error = repr(exc)
                    continue
                results[winner or "unfinished"] += 1
                turns.append(n)
            avg = sum(turns) / len(turns) if turns else 0
            print(f"{difficulty:>4} AI, {num_ai} opponent(s): {dict(results)}, "
                  f"average turns {avg:.1f}, errors {errors}")
            if errors:
                print("   last error:", last_error)


if __name__ == "__main__":
    main()
