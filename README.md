# Notty: a card game with AI opponents

A desktop card game written in Python with pygame. You play against one or two computer players, with an easy and a hard difficulty. It was built as a group project for COMP4008 Programming (University of Nottingham, 2025-26).

**My part:** I wrote the game engine (`notty/element_action/game.py`), which runs the whole game: turn order, action rules, group checks, win detection and the AI turns. I also built the winner screen: a darkened, blurred background with an animated message and sound, where a click starts a new game.

## The game

- 90 cards: five colours (red, green, yellow, black, blue), numbered 1 to 9, two of each. Two or three players, four cards each, all face up.
- On your turn you can, in any order:
  1. draw up to 3 cards (once per turn),
  2. steal a random card from another player (once per turn),
  3. draw one card and then discard one (once per turn),
  4. discard a valid group as many times as you like: a run of at least three cards of one colour with consecutive numbers, or a set of at least four cards with the same number and different colours.
- A hand can never hold more than 20 cards. Discarded cards go back into the deck, which is reshuffled.
- The first player with no cards left wins.

## How it is built

| Part | File | What it does |
|---|---|---|
| Cards and deck | `notty/element_action/card.py` | `Card` and `Deck` (create, shuffle, draw) |
| Players | `notty/element_action/player.py` | `Player`, plus `AIPlayer` (hard) and `EasyAIPlayer` (easy) that score cards, find runs and sets, and choose whether to draw, steal or discard |
| Game engine | `notty/element_action/game.py` | `GameEngine`: deals cards, enforces the rules with turn flags, validates groups, checks for a win, runs the AI turns |
| Interface | `notty/ui/` | pygame screens, buttons, card animations and the winner pop-up |
| Start-up | `notty/main.py` | window, frame loop and event handling |

The engine does not depend on pygame, so it can be tested without a window.

## Run it

1. Install Python 3 (3.12 was used for the coursework) and the one dependency: `pip install -r requirements.txt`
2. From the main folder of this repository, run: `python notty/main.py`
3. Press `Esc` to quit.

The game opens a 1920 x 1080 window.

## Check the engine

`simulate_games.py` plays many full games without opening a window and reports any engine errors.

```
python simulate_games.py        # 100 games for each setting
python simulate_games.py 500    # choose how many
"unfinished" means nobody won within 400 turns. The easy AI plays loosely, so many of its games never finish. The hard AI wins about a third of games within that limit.
```

In my runs of 100 games for each setting (easy and hard AI, one and two opponents) there were no engine errors.

## Repository contents

| Path | What it is |
|---|---|
| `notty/` | The game: engine, players, interface and images |
| `simulate_games.py` | Headless engine check |
| `docs/engine-notes.pdf` | My notes on how the engine works and what I built |
| `requirements.txt` | Python dependency (pygame) |
