"""Shows the winner screen without having to win a game.

Run from the main folder of the repository:
    python preview_winner_popup.py            # "You" win
    python preview_winner_popup.py NPC 1      # NPC 1 wins (also try NPC 2)

Click anywhere on the winner screen to start a new game, or press Esc to quit.
"""
import sys

import notty.main as game  # opens the game window and builds the interface

winner = " ".join(sys.argv[1:]) or "You"
game.ui.check_game_over({"winner": winner})  # the same call the game makes when someone wins
game.main()
