# DDR Bomb - Rhythm Arcade Game

[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/Engine-pygame--ce-purple.svg)](https://pyga.me/)
[![Branch](https://img.shields.io/badge/Branch-Game-orange.svg)](https://github.com/)

---

## 1. Project Overview

**DDR Bomb** is a Dance Dance Revolution-inspired arcade rhythm game developed in Python using `pygame-ce`. Colorful arrow notes cascade down four distinct tracks toward target receptors at the bottom of the screen.

Players must hit corresponding keyboard arrow keys in rhythm while actively avoiding lethal **Bomb Arrows** that detonate on contact. The game integrates a bilingual selection system at startup (**English on top, Español on bottom**), real-time combo multipliers, an emotional purple avatar, and smooth 60 FPS gameplay.

---

## 2. Key Game Features

- **Integrated Bilingual Selection**: Displays a clean selection screen upon game startup (English / Español) with real-time translation for all HUD elements, floating text, and game-over summaries.
- **Rhythm Strike Mechanics**: Four directional lanes (Left ←, Down ↓, Up ↑, Right →) featuring calibrated timing windows (`PERFECT` and `GOOD`).
- **Hazard Obstacles (Bomb Arrows)**: Dark arrow bodies flashing with dynamic sinusoidal red warnings and sparks. Hitting a bomb causes an instant explosion and ends the session; safely letting it pass awards +25 bonus score.
- **Combo & Multiplier Scaling**: Consecutive hits build combos and multiply earned score up to $4\times$.
- **Procedural Difficulty Progression**: Falling speeds, spawn rates, bomb hazard ratios, and simultaneous double notes escalate progressively as the player levels up.
- **Purple Player Theme**: Both the strike receptors at the bottom and the animated emotional companion avatar are rendered in purple (`RGB: 150, 60, 230`).
- **Regulated 60 FPS Clock**: Smooth gameplay governed by `pygame.time.Clock()` with delta-time safety capping.

---

## 3. Repository Branch Architecture

The project is structured across the following branches:

```
RP_Li_Bastero_Gomez_25
├── main             # Base branch
├── Game             # Main deliverable branch containing game.py and documentation
└── ROS              # Reserved workspace for subsequent robotics laboratories
```

---

## 4. Installation & Requirements

### Prerequisites
- Python 3.10 or higher
- `pygame-ce` (Community Edition)

### Dependencies Installation
Run the following command in your terminal:
```bash
pip install pygame-ce
```

---

## 5. How to Run & Controls

### Launching the Game
Execute the main game script located in the `Game` branch:
```bash
python game.py
```
*(On Windows systems with the Python launcher installed, you can also run `py game.py`)*

### Control Schemes

| Screen Context | Key / Action | Functionality |
| :--- | :--- | :--- |
| **Language Select** | `↑` / `↓` or `W` / `S` | Navigate between English and Español |
| | `ENTER` / `SPACE` | Confirm language selection |
| | `1` or `2` | Quick shortcut (1: English, 2: Español) |
| | Left Mouse Click | Directly click on language card |
| **Welcome Screen** | Any Key (Space/Enter) | Start the game |
| | `L` | Re-open language selection menu |
| | `ESC` | Exit game |
| **Gameplay** | `←` (Left Arrow) | Strike Lane 1 (Left) |
| | `↓` (Down Arrow) | Strike Lane 2 (Down) |
| | `↑` (Up Arrow) | Strike Lane 3 (Up) |
| | `→` (Right Arrow) | Strike Lane 4 (Right) |
| | `ESC` | Quit session |
| **Game Over** | `ENTER` / `SPACE` | Restart game |
| | `L` | Change language |
| | `ESC` | Exit game |

---

## 6. Timing Windows & Scoring Mechanics

- **Target Line Coordinate**: $y = 570\text{ px}$ (Screen Height: $700\text{ px}$)
- **PERFECT**: Distance $\le 25\text{ px} \implies +100 \times \text{Multiplier}$
- **GOOD**: $25\text{ px} < \text{Distance} \le 75\text{ px} \implies +50 \times \text{Multiplier}$
- **TOO EARLY**: Pressed when no arrow is within $75\text{ px} \implies \text{Combo resets}$
- **MISS**: Note crosses bottom boundary without input $\implies -1\text{ Life}$, combo resets
- **BOMB DODGED**: Bomb arrow safely exits bottom screen $\implies +25\text{ Bonus points}$
- **BOMB DETONATED**: Pressing a bomb arrow $\implies \text{Instant explosion and game over}$

---

## 7. State Machine Workflow

```
[Game Launch]
      │
      ▼
[STATE_LANGUAGE] ──(Choose EN / ES)──► [STATE_WELCOME]
                                             │
                                        (Press Key)
                                             │
                                             ▼
                                      [STATE_PLAYING]
                                        │         │
                        (Deplete Lives) │         │ (Hit Bomb)
                                        ▼         ▼
                                 [STATE_GAME_OVER]
                                    │          │
                       (Enter/Space)│          │ (Press 'L')
                                    ▼          ▼
                             [STATE_PLAYING]  [STATE_LANGUAGE]
```

---

## 8. Compliance with Course Assessment Criteria

This implementation satisfies all 10 development specifications outlined in `DELIVERABLE.GAME_AI_PR.pdf` (Page 3):

| Item | Requirement Description | Implementation in DDR Bomb | Code Reference |
| :---: | :--- | :--- | :--- |
| **2** | **Welcome Screen** | Displays game title, controls, bomb warning, and waits for player keypress. | `draw_welcome()` |
| **3** | **Player Control** | 4-lane input mapped to keyboard arrow keys (`←`, `↓`, `↑`, `→`). | `press_lane()`, `KEY_TO_LANE` |
| **4** | **Obstacles or Enemies** | Automatically descending Bomb Arrows with pulsating red danger rings. | `draw_bomb_arrow()`, `Note` |
| **5** | **Collisions** | Detonating a bomb causes instant failure; missing regular notes loses lives. | `press_lane()`, `end_game()` |
| **6** | **Score System** | Points awarded for timing precision (Perfect/Good) with combo scaling up to 4x. | `multiplier()`, `register_resolved()` |
| **7** | **Current Score** | Permanent HUD displaying real-time score, level, lives, and combo status. | `draw_hud()` |
| **8** | **End Game Screen** | Summarizes final score, personal best, cause of death, and replay/exit prompts. | `draw_game_over()` |
| **9** | **Increasing Difficulty** | Falling speeds (260–820 px/s), spawn intervals, and bomb rates scale with levels. | `fall_speed()`, `spawn_interval()` |
| **10** | **Player Visible in Purple**| Strike receptors and animated companion avatar are rendered in vibrant purple. | `PURPLE`, `draw_avatar()` |
| **11** | **Size of the Screen** | Fixed, consistent window dimensions of $800 \times 700\text{ px}$. | `SCREEN_WIDTH`, `SCREEN_HEIGHT` |
