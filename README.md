# Notty: A Python Card Game with AI Opponents 🃏

A desktop card game developed in Python using Pygame. Players compete against one or two computer-controlled opponents, with Easy and Hard AI difficulty levels.

This project was developed as a group coursework project for **COMP4008 Programming (University of Nottingham, 2025–26)**.

### My Individual Contribution

My main contribution was developing the **game engine** (`notty/element_action/game.py`), which controls the core gameplay logic, including:

- Managing player turn order and game flow.
- Implementing card drawing, stealing and discarding rules.
- Validating card groups (runs and sets).
- Checking winning conditions.
- Managing AI turns and game actions.

I also developed the **winner screen**, including the darkened background, animated "YOU WIN!" message, winner image and sound effect. Players can click to start a new game.

### 🎮 The Game

- 90 cards across five colours: red, green, yellow, black and blue.
- Numbers range from 1 to 9, with two copies of each card.
- Supports two or three players, with four cards dealt to each player.
- Play against Easy or Hard AI opponents.

On each turn, players can:
1. Draw up to three cards (once per turn).
2. Steal a random card from another player (once per turn).
3. Draw one card and discard one card (once per turn).
4. Discard valid groups as many times as possible:
   - **Runs:** At least three consecutive numbers of the same colour.
   - **Sets:** At least four cards with the same number but different colours.

A hand can contain a maximum of 20 cards. Discarded cards return to the deck, which is reshuffled.

The first player to discard all their cards wins.

### 🛠️ How It Is Built

| Component | File | Description |
|---|---|---|
| Cards and Deck | `notty/element_action/card.py` | Card creation, deck management, shuffling and drawing |
| Players and AI | `notty/element_action/player.py` | Player logic and Easy/Hard AI decision-making |
| Game Engine | `notty/element_action/game.py` | Turn management, game rules, group validation and win detection |
| User Interface | `notty/ui/` | Pygame screens, buttons, animations and winner screen |
| Main Application | `notty/main.py` | Game window, event handling and main loop |

The game engine is independent of Pygame, allowing its core logic to be tested without launching the graphical interface.

### 🚀 How to Run

**Requirements:** Python 3 (Python 3.12 was used for the coursework).

1. Clone or download this repository.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the game:

   ```bash
   python notty/main.py
   ```

4. Press `Esc` to quit.

The game opens in a 1920 × 1080 window.

### 🧪 Engine Testing

The `simulate_games.py` script runs complete games without opening the Pygame interface. It helps check the game engine and identify errors during gameplay.

Run the default simulation:

```bash
python simulate_games.py
```

Run a larger simulation:

```bash
python simulate_games.py 500
```

In my testing, 100 games were simulated for each configuration (Easy and Hard AI, with one and two opponents), with no engine errors reported.

### 📁 Repository Contents

| Path | Description |
|---|---|
| `notty/` | Main game package, including the engine, players, AI, interface and images |
| `notty/element_action/` | Card, player and game-engine logic |
| `notty/ui/` | Pygame interface and visual components |
| `simulate_games.py` | Headless engine simulation and testing |
| `preview_winner_popup.py` | Standalone winner-popup preview script |
| `docs/engine-notes.pdf` | Technical notes explaining the game engine and my implementation |
| `requirements.txt` | Python dependency (Pygame) |
| `.gitignore` | Files and folders excluded from version control |
| `README.md` | Project documentation |

### 💡 What I Learned

Through this project, I gained practical experience in:

- Object-oriented programming and class design.
- Implementing game logic and managing complex state transitions.
- Developing AI opponents with different difficulty levels.
- Building graphical interfaces and animations using Pygame.
- Testing game engines independently of graphical interfaces.
- Collaborating on a group software development project.
