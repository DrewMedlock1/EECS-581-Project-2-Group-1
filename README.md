<!--
# Course: EECS 581: Software Engineering II
# Project: Minesweeper (Project 2 - Enhance Another Team's Minesweeper System)
# Description: Project overview, setup and controls, AI solver rules, custom
#              timer/leaderboard feature, system architecture and UML diagrams.
# Inputs:
#     The current minesweeper.py source and documentation/NewUML.md diagrams.
# Outputs:
#     Repository README rendered by GitHub, including Mermaid UML diagrams.
# Author: Kyler Russell
# Source attribution: Created with the assistance of Claude (Opus 5.5). The
#                     diagrams are adapted from documentation/NewUML.md by
#                     Carter Steenhard.
# Date: 10/11/2026
-->

# Minesweeper with an AI Solver

A Python/Pygame Minesweeper game for **EECS 581 Software Engineering II (Fall 2026), Project 2**.
Our team (Group 1) inherited Group 2's Project 1 Minesweeper and extended it on top of the original code. We:

- fixed the Project 1 requirements that were missing or buggy,
- added an **AI solver** with Easy, Medium and Hard difficulties that can take turns with you or play on its own, and
- added a **custom feature**: a game timer with a local leaderboard of the fastest wins for each mine count.

All game code is in one module, [`EECS-581-Project-1-Group-2/minesweeper.py`](EECS-581-Project-1-Group-2/minesweeper.py).

---

## Contents

- [Running the game](#running-the-game)
- [How to play](#how-to-play)
- [AI solver](#ai-solver)
- [Custom addition: timer and leaderboard](#custom-addition-timer-and-leaderboard)
- [System architecture](#system-architecture)
- [UML diagrams](#uml-diagrams)
- [Key data structures](#key-data-structures)
- [Extending the system](#extending-the-system)
- [Repository layout](#repository-layout)
- [Authors and attribution](#authors-and-attribution)

---

## Running the game

**Requirements:** Python 3 (developed with Python 3.12) and **pygame 2.0.1 or newer**.

```bash
pip install pygame
python EECS-581-Project-1-Group-2/minesweeper.py
```

The game finds its font and images relative to `minesweeper.py`, so you can run it from any folder. The window can be resized and the game scales with it.

---

## How to play

### 1. Set up a game

The game opens on a setup menu:

| Setting | Options |
| --- | --- |
| Number of mines | 10 to 20. Type a number, or use the Up and Down arrows. **Start Game** stays disabled until the number is valid. |
| AI type | **Manual**: no AI. **Interactive**: you and the AI take turns. **Automatic**: the AI plays by itself. |
| AI difficulty | **Easy**, **Medium** or **Hard**. Shown only when an AI type is chosen. |

Press **Start Game** (or Enter) to begin. The **Leaderboard** button shows saved best times.

### 2. Play

The board is a 10 × 10 grid with columns labeled **A–J** and rows labeled **1–10**. Your first click is always safe, and so are the 8 tiles around it, so every game starts with an opening.

| Input | Action |
| --- | --- |
| Left click | Open a tile. A number shows how many mines touch it, and a blank tile opens its neighbors automatically. |
| Right click | Place or remove a flag |
| **R** | Restart with the same settings |
| **M** | Return to the setup menu (after a win or loss) |
| **L** | Open the leaderboard |
| **E** | Turn AI play on or off (uses the chosen difficulty, or Easy) |
| **?** button, **I** or **?** | Open the controls help box (pauses the timer) |

Below the board the game shows the elapsed time, whose turn it is (in AI games), **Mines remaining** (mines minus flags placed) and a status line: *Playing*, *Victory*, *Game Over: Loss*, or the AI mode during AI games.

### 3. End of the game

- **Loss:** opening a mine ends the game and reveals every mine.
- **Win:** opening every tile without a mine wins, and all mines are flagged automatically.

After either one, press **R** to play again with the same settings or **M** to go back to the menu.

---

## AI solver

The AI plays on the same board as the player, and all of its moves go through the same `open_tile()` / `flag_tile()` helpers. Mine placement, flood fill, the timer, and win/loss checks therefore work the same no matter who moves.

**Modes**

- **Interactive:** each player move (a reveal or a flag change) is answered by one AI move a second later. Clicks are ignored while the AI is taking its turn.
- **Automatic:** the AI makes one move per second until the game is won or lost. Player clicks are ignored.

**Difficulties**

| Level | Strategy |
| --- | --- |
| Easy | Opens a random tile that is not open and not flagged. |
| Medium | Goes through the revealed numbers and applies the first rule that works: **(1)** if the number of covered neighbors (hidden plus flagged) equals the number, flag all the hidden ones; **(2)** if the number of flagged neighbors equals the number, open the remaining hidden ones. If no rule applies, it opens a random hidden tile. |
| Hard | Medium's rules, then the **1-2-1 pattern**: three side-by-side revealed tiles reading 1-2-1, with every covered neighbor in the single line of tiles on one side, mean the two outer tiles of that line are mines (flagged) and the middle one is safe (opened). If nothing applies, it opens a random tile. |

The AI trusts the flags on the board, so in interactive mode a wrong flag placed by the player can lead Medium or Hard into a mine. In headless tests over thousands of automatic games, the AI never placed a wrong flag on its own, and every AI loss came from a random guess, not from a rule.

---

## Custom addition: timer and leaderboard

- **Timer:** starts on the first reveal and stops on a win or loss, after which the exact final time stays on screen.
- **Leaderboard:** keeps the 10 fastest wins **for each mine count** (10–20), so a win is compared only with games that had the same number of mines. Only games won **without AI help** count; games started in an AI mode or helped with **E** are excluded.
- **Name entry:** a qualifying win asks for a name of up to 8 letters, digits or spaces. Esc skips saving.
- **Storage:** scores are saved to `leaderboard.json` next to `minesweeper.py`. The file is created when first needed and is ignored by git. A missing or damaged file starts an empty leaderboard instead of crashing.

The full UML sequence diagram for this feature is [below](#custom-addition-sequence-diagram).

---

## System architecture

`minesweeper.py` is one Pygame program built around a main loop. Each frame, the loop sends input to whichever screen is active and redraws that screen at up to 60 FPS. The screens are the **setup menu**, the **game board**, and three overlays: **name entry**, **leaderboard** and **controls help**. The logical components are:

| Component | Responsibility | Main functions |
| --- | --- | --- |
| Main loop and events | Sends mouse, keyboard, timer and quit events to the active screen | `while True` loop at the bottom of the file |
| Setup menu | Mine count, AI mode and difficulty; starts a game | `drawSelection`, `handle_selection_event`, `start_game`, `return_to_menu` |
| Shared game logic | The single path for every reveal and flag, used by the player and the AI | `open_tile`, `flag_tile`, `reveal_tile`, `set_bombs`, `check_win`, `reset_game` |
| Board state | 10 × 10 grid of `Tile` objects plus win/loss flags | `board`, `Tile`, `game_over`, `game_won` |
| AI timing and strategies | Schedules AI moves with Pygame timer events and picks moves | `start_ai_timer`, `schedule_ai_turn`, `handle_ai_event`, `easy/medium/hard_AI_action`, `apply_basic_rules`, `apply_121_rule` |
| Game timer | Measures game duration | `start_timer`, `stop_timer`, `elapsed_seconds` |
| Leaderboard | Eligibility, ranking, name entry and the JSON file | `handle_win`, `add_leaderboard_entry`, `load_leaderboard`, `save_leaderboard`, `drawLeaderboard` |
| Controls help | Lists the controls; pauses the timer and holds AI turns while open | `open_info`, `close_info`, `drawInfo` |
| Rendering | Draws the board, labels, footer text and overlays | `drawBoard`, `draw_game_status`, `draw_button`, `draw_text_centered` |

**Data flow:** player input or an `AI_event` leads to `open_tile()` / `flag_tile()`. These update the `Tile` states in `board`, start or stop the timer, and on a manual win call `handle_win()`, which may write `leaderboard.json`. The next frame then draws the new state.

---

## UML diagrams

These Mermaid diagrams render directly on GitHub. [`documentation/NewUML.md`](documentation/NewUML.md) has the same diagrams with more notes.

### System architecture overview

```mermaid
flowchart TD
    Player[Player]
    Events["Pygame events and main loop"]
    Menu["Selection screen<br/>mine count, AI mode and difficulty"]
    Moves["Shared game logic<br/>open_tile, flag_tile, reset_game"]
    Board["Shared board and game state<br/>10 x 10 Tile objects, win/loss flags"]
    AI["AI timing and strategies<br/>easy, medium and hard"]
    Timer["Game timer<br/>start_timer, stop_timer, elapsed_seconds"]
    Scores["Leaderboard and name entry<br/>eligibility, ranking and persistence"]
    Rendering["Pygame rendering<br/>board, menu, timer, status and rankings"]
    Assets["assets/<br/>font and tile images"]
    Help["Controls help box<br/>open_info, close_info, drawInfo"]
    Disk[("leaderboard.json<br/>name, time and mines")]

    Player -->|mouse and keyboard input| Events
    Events -->|selection input| Menu
    Menu -->|start_game applies settings| Moves
    Events -->|player moves and restart| Moves
    Events -->|AI_event| AI
    Board -->|visible tile states| AI
    AI -->|reveal or flag decisions| Moves
    Moves -->|creates and updates tiles and flags| Board
    Moves -->|first reveal and game end| Timer
    Moves -->|winning game calls handle_win| Scores
    Timer -->|final_time| Scores
    Events -->|name entry and leaderboard controls| Scores
    Scores -->|save ranked entries| Disk
    Disk -->|load saved entries at startup| Scores
    Board -->|tile states, mine count and game status| Rendering
    Timer -->|elapsed or final time| Rendering
    Scores -->|name prompt and ranked entries| Rendering
    Menu -->|selection values and controls| Rendering
    Assets -->|font and images| Rendering
    Events -->|M after a win or loss: return_to_menu| Menu
    Events -->|? button, I or ? key| Help
    Help -->|pauses timer while open| Timer
    Help -->|re-schedules a held AI turn| AI
    Help -->|control list for this game| Rendering
    Rendering -->|graphical display| Player
```

### Module and tile structure (class diagram)

`Tile` is the only class. The game state and functions are module-level members of `minesweeper.py`.

```mermaid
classDiagram
    direction LR
    class Minesweeper["minesweeper.py"] {
        <<module>>
        board : list of lists of Tile
        boardSize : int = 10
        max_num_of_bombs : int = 10
        bombs_placed : bool
        game_over : bool
        game_won : bool
        AI_mode : str
        AI_difficulty : str
        AI_type : str
        AI_on : bool
        ai_turn_pending : bool
        ai_used : bool
        game_start_ticks : int or None
        final_time : float or None
        leaderboard : list of dict
        in_selection : bool
        entering_name : bool
        showing_leaderboard : bool
        showing_info : bool
        start_game()
        return_to_menu()
        reset_game()
        open_tile(tile)
        flag_tile(tile)
        handle_ai_event()
        do_AI_action()
        handle_win()
        open_info()
        close_info()
        drawBoard(mouseTile)
        draw_game_status()
    }
    class Tile {
        x : int
        y : int
        rect : pygame.Rect
        state : int = -1
        has_bomb : bool = False
        __init__(x, y)
    }
    class Pygame {
        <<external_library>>
        display
        event
        time
        font
        image
        draw
    }
    class Rect["pygame.Rect"] {
        <<external_class>>
        collidepoint(pos)
    }
    class Random["random"] {
        <<standard_library>>
        sample(population, k)
        choice(sequence)
        uniform(a, b)
    }
    class Persistence["json / pathlib.Path"] {
        <<standard_library>>
        loads(text)
        dumps(value, indent)
        read_text()
        write_text(text)
    }
    class LeaderboardFile["leaderboard.json"] {
        <<runtime_file>>
        name : str
        time : float
        mines : int
    }
    class Assets["assets/"] {
        <<directory>>
        Minesweeper.ttf
        tile images
    }
    Minesweeper "1" *-- "100" Tile : board[y][x]
    Tile "1" *-- "1" Rect : rect
    Minesweeper ..> Pygame : input, drawing and timers
    Minesweeper ..> Random : bomb placement and AI guesses
    Minesweeper ..> Persistence : loads and saves leaderboard
    Minesweeper ..> LeaderboardFile : reads and writes
    Minesweeper ..> Assets : loads font and images
```

### Custom addition sequence diagram

The timer and leaderboard flow, from startup through a loss, an AI-assisted win, a time that doesn't qualify, and a saved score.

```mermaid
sequenceDiagram
    actor Player
    participant GameLoop as Main loop and screen handlers
    participant Moves as Shared game logic
    participant GameTimer as Game timer functions
    participant Scores as Leaderboard functions
    participant Disk as leaderboard.json

    GameLoop->>Scores: load_leaderboard() at startup
    Scores->>Disk: Read saved JSON entries
    Note over Scores,Disk: Missing or unreadable file returns an empty list<br/>Malformed entries are skipped and rankings are trimmed
    Scores-->>GameLoop: Ranked entries in memory

    Player->>GameLoop: First left click on covered tile
    GameLoop->>Moves: open_tile(tile)
    Moves->>Moves: set_bombs(board, tile) with safe first-click neighborhood
    Moves->>GameTimer: start_timer()
    GameTimer->>GameTimer: Record game_start_ticks
    Moves->>Moves: Reveal safe tile and check_win()

    loop Each game frame until a win or loss
        GameLoop->>GameTimer: elapsed_seconds()
        GameTimer-->>GameLoop: Elapsed duration
        GameLoop-->>Player: Draw timer with board and status
    end

    alt A later reveal hits a mine
        GameLoop->>Moves: open_tile(tile)
        Moves->>Moves: reveal_bombs() and set game_over
        Moves->>GameTimer: stop_timer()
        GameTimer->>GameTimer: Store final_time
        GameLoop-->>Player: Show loss and final time without saving an entry
    else Last safe tile is revealed
        GameLoop->>Moves: open_tile(tile)
        Moves->>Moves: check_win(), flag_bombs() and set game_won
        Moves->>Scores: handle_win()
        Scores->>GameTimer: stop_timer()
        GameTimer->>GameTimer: Store final_time
        alt AI was used
            Note over Scores: Do not request a name or add a leaderboard entry
            GameLoop-->>Player: Show victory and final time
        else No AI was used
            Scores->>Scores: qualifies_for_leaderboard(final_time, max_num_of_bombs)
            alt Time does not qualify
                GameLoop-->>Player: Show victory and final time without name entry
            else Time qualifies
                Scores->>Scores: Set entering_name and clear name_input_text
                GameLoop-->>Player: drawNameEntry() with winning time
                alt Player presses Esc
                    Player->>GameLoop: Skip saving
                    GameLoop->>GameLoop: Clear entering_name
                    GameLoop-->>Player: Return to won board
                else Player presses Enter
                    Player->>GameLoop: Submit name
                    Note over GameLoop: Blank name defaults to Player<br/>Input accepts up to 8 letters, digits or spaces
                    GameLoop->>Scores: add_leaderboard_entry(name, final_time, mines)
                    Scores->>Scores: Round time to 2 decimals and keep_top_times()
                    Scores->>Disk: save_leaderboard() writes JSON
                    Note over Scores,Disk: Write errors are printed<br/>The in-memory rankings remain available
                    Scores-->>GameLoop: New entry row for highlighting
                    GameLoop->>Scores: open_leaderboard(mines, row)
                    GameLoop-->>Player: drawLeaderboard() with highlighted entry
                end
            end
        end
    end
```

### Game and screen states

```mermaid
stateDiagram-v2
    state "Controls help box" as Info
    [*] --> Selection : initialize Pygame, assets, board and leaderboard
    Selection --> Game : start_game() / valid mine count and selected AI settings

    state Game {
        [*] --> Ready
        Ready --> Playing : first open_tile() / set_bombs(), start_timer()
        Playing --> Lost : open_tile() hits bomb / reveal_bombs(), stop_timer()
        Playing --> Won : check_win() / flag_bombs(), handle_win()
        Ready --> Ready : R / reset_game()
        Playing --> Ready : R / reset_game()
        Lost --> Ready : R / reset_game()
        Won --> Ready : R / reset_game()
    }

    Won --> Selection : M / return_to_menu()
    Lost --> Selection : M / return_to_menu()
    Won --> NameEntry : no AI used and time qualifies
    NameEntry --> Leaderboard : Enter / add_leaderboard_entry(), open_leaderboard()
    NameEntry --> Won : Esc / skip saving
    Selection --> Leaderboard : leaderboard button
    Game --> Leaderboard : L / open_leaderboard()
    Leaderboard --> Leaderboard : Left or Right / change mine count
    Game --> Info : ? button, I or ? key / open_info()
    Info --> Game : any key or click / close_info(), same board
    Leaderboard --> ReturnScreen : other key or mouse click / close overlay
    state ReturnScreen <<choice>>
    ReturnScreen --> Selection : in_selection
    ReturnScreen --> Game : game screen underneath, keep existing board and flags
```

### Interactive AI turn

```mermaid
sequenceDiagram
    actor Player
    participant GameLoop as Main loop
    participant Moves as Shared move helpers
    participant Timer as Pygame AI timer
    participant AI as AI functions
    participant Win as Timer and leaderboard functions

    Player->>GameLoop: Mouse button released on tile
    Note over GameLoop: Ignore clicks in automatic mode,<br/>during a pending AI turn, or after loss
    alt Left click on covered tile
        GameLoop->>Moves: open_tile(tile)
        Note over Moves: Ignore flagged, revealed and post-game tiles
        opt First reveal
            Moves->>Moves: set_bombs(board, tile)
            Moves->>Win: start_timer()
        end
        alt Tile has bomb
            Moves->>Moves: reveal_bombs()<br/> game_over = True
            Moves->>Win: stop_timer()
        else Safe tile
            Moves->>Moves: reveal_tile(tile)<br/> check_win()
            opt All safe tiles revealed
                Moves->>Moves: flag_bombs()<br/> game_won = True
                Moves->>Win: handle_win()
                Win->>Win: stop_timer()<br/> check leaderboard eligibility
            end
        end
    else Right click on covered or flagged tile
        GameLoop->>GameLoop: Toggle tile.state between -1 and -2
    end

    opt Board changed, interactive mode, and game still active
        GameLoop->>AI: schedule_ai_turn()
        AI->>Timer: set_timer(AI_event, 1000, loops=1)
        Note over GameLoop,AI: ai_turn_pending blocks further player clicks
        Timer-->>GameLoop: AI_event
        GameLoop->>AI: handle_ai_event()
        AI->>AI: Clear pending turn<br/> do_AI_action()
        alt Easy
            AI->>AI: random_hidden_tile()
            AI->>Moves: open_tile(tile) if one exists
        else Medium
            AI->>AI: apply_basic_rules()<br/> random reveal if no rule applies
            AI->>Moves: flag_tile(tile) or open_tile(tile)
        else Hard
            AI->>AI: Basic rules, then 1-2-1 rule, then random reveal
            AI->>Moves: flag_tile(tile) or open_tile(tile)
        end
        opt AI move ends game
            AI->>AI: stop_ai_timer()
            AI->>Timer: Cancel timer and clear queued AI events
        end
    end
```

---

## Key data structures

**`board`** is a list of 10 rows, each holding 10 `Tile` objects, and is indexed **`board[y][x]`** (row first).

**`Tile`** has `x`, `y`, `rect` (its `pygame.Rect` on screen), `has_bomb`, and `state`:

| `state` | Meaning |
| --- | --- |
| `-1` | Covered |
| `-2` | Flagged |
| `-3` | Revealed mine (game lost) |
| `0` | Revealed blank |
| `1`–`8` | Revealed number of neighboring mines |

**Leaderboard entry** (one item in the list saved to `leaderboard.json`):

```json
{ "name": "ExampleName", "time": 42.17, "mines": 12 }
```

**Main game flags:** `in_selection`, `game_over`, `game_won`, `bombs_placed`, `AI_mode` (`manual` / `interactive` / `automatic`), `AI_type` (`easy` / `medium` / `hard`), `AI_on`, `ai_turn_pending`, `ai_used`, `game_start_ticks`, `final_time`, `showing_leaderboard`, `entering_name`, `showing_info`.

---

## Extending the system

The timer and leaderboard are the feature our team added, so this section explains how they work inside `minesweeper.py` and how to change them safely. The code is in the *"Local leaderboard"* section of the file, with the timer functions near `reset_game()`.

### How the leaderboard works

1. **Startup:** `leaderboard = load_leaderboard()` reads `leaderboard.json` into memory as a list of `{name, time, mines}` dictionaries. A missing or unreadable file gives an empty list, and malformed entries are skipped one at a time, so a bad file never stops the game.
2. **Timing:** the first reveal of a game (in `open_tile()`) calls `start_timer()`, which records `game_start_ticks`. A loss or win calls `stop_timer()`, which stores `final_time`. `elapsed_seconds()` is what the footer displays. The controls help box pauses the timer by moving `game_start_ticks` forward when it closes.
3. **Win check:** `open_tile()` calls `handle_win()`. It asks for a name only if the game had no AI help (`ai_used` is `False`) and `qualifies_for_leaderboard(final_time, mines)` is true. That means the list for this mine count has fewer than `LEADERBOARD_SIZE` entries, or the time is **strictly faster** than the current last place.
4. **Name entry:** `entering_name` switches the main loop to `drawNameEntry()` / `handle_name_entry_event()`. Enter saves (a blank name becomes "Player") and Esc skips.
5. **Saving:** `add_leaderboard_entry()` rounds the time to 2 decimals, appends it, calls `keep_top_times()` to sort and trim each mine count's list, writes the file with `save_leaderboard()`, and returns the new entry's row so it can be highlighted.
6. **Viewing:** `open_leaderboard(mines, highlight)` sets `showing_leaderboard`, and the main loop then draws `drawLeaderboard()` over the current screen. Left and Right change `leaderboard_mines`; any other key or click closes it. It opens from the menu button, the **L** key, and after a saved win.

| Function / value | Role |
| --- | --- |
| `LEADERBOARD_FILE` | Where scores are stored (`leaderboard.json` next to `minesweeper.py`) |
| `LEADERBOARD_SIZE` (10) | How many times are kept for each mine count |
| `NAME_MAX_LENGTH` (8) | Longest name allowed on the name entry screen |
| `keep_top_times(entries)` | Stable sort by time (earlier ties stay ahead) and trim to `LEADERBOARD_SIZE` for each mine count |
| `times_for_mines(mines)` | One mine count's ranked list, fastest first |
| `qualifies_for_leaderboard(seconds, mines)` | Whether a time would make that mine count's list |
| `load_leaderboard()` / `save_leaderboard()` | The only two functions that touch the file |
| `handle_win()` | Stops the timer and decides whether to ask for a name |
| `ai_used` | Set by `reset_game()` for AI modes and by the **E** key; blocks leaderboard entry |

### Common changes

**Keep more or fewer times.** Change `LEADERBOARD_SIZE`. The screen fits **13 rows** (rows are 13 px apart starting at `header_y + 14`), so going past 13 needs a smaller row spacing, a taller window, or scrolling in `drawLeaderboard()`.

**Allow longer names.** Change `NAME_MAX_LENGTH`. Names start at `name_x = 30` and times are right-aligned at `windowWidth - 14`, so there is room for about 12 wide characters before a name runs into the time column.

**Add a field to each entry** (for example the date of the win). Make the change in three places, and give old entries a default so existing `leaderboard.json` files still load:

```python
import datetime   # at the top of the file

# add_leaderboard_entry(): store the new field
entry = {'name': name, 'time': round(seconds, 2), 'mines': mines,
         'date': datetime.date.today().isoformat()}

# load_leaderboard(): read it with a default for entries saved before the change
'date': str(entry.get('date', '')),

# drawLeaderboard(): add a column, e.g. with draw_text_aligned(entry['date'], ...)
```

**Rank by something other than mine count** (for example board size or difficulty, if those are added). Entries are grouped by `entry['mines']` in three places: `keep_top_times()`, `times_for_mines()` and `qualifies_for_leaderboard()`. The screen pages through mine counts using `leaderboard_mines`, `MIN_MINES` and `MAX_MINES`. Replace those with a shared key, such as a `leaderboard_key(entry)` helper returning `(mines, board_size)`, and update the Left/Right paging in `handle_leaderboard_event()` to step through the keys.

**Track AI scores separately.** AI-assisted wins are currently thrown away by the `not ai_used` check in `handle_win()`. To keep them, store an `ai` field (`AI_type` or `None`) with each entry, include it in the grouping key above, and remove the check.

**Use a different storage location or an online leaderboard.** Only `load_leaderboard()` and `save_leaderboard()` read or write the file, and the rest of the game uses the in-memory `leaderboard` list. Replace those two functions (for example, with calls to a web service) and keep two rules: return the same list of `{name, time, mines}` dictionaries, and catch every error and fall back to an empty or unchanged list so a network or disk problem never crashes the game. Keep any slow request out of the 60 FPS main loop (load once at startup, save only after a win).

**Testing changes.** Delete `leaderboard.json` to start from an empty leaderboard. To check that bad data is handled, put malformed JSON or entries with missing fields in the file and make sure the game still starts. Remember that a win only counts in **Manual** mode without pressing **E**.

### Other extension points

- **New AI strategy:** write a function that uses `open_tile()` / `flag_tile()` and returns `True` when it made a move. Call it from an `*_AI_action()` function, or add a new difficulty to `do_AI_action()`, `AI_DIFFICULTIES` and `AI_DIFFICULTY_LABELS`.
- **New overlay screen:** follow the leaderboard and help box pattern: a `showing_*` flag, a draw function, an event handler, and a branch in the main loop. If the overlay can open mid-game, re-schedule a pending interactive AI turn when it closes, as `close_info()` does.

---

## Repository layout

```
EECS-581-Project-1-Group-2/
    minesweeper.py           the game
    assets/                  pixel font and tile images
    README.md                original Project 1 README
documentation/
    NewUML.md                architecture overview and UML diagrams
    estimated-hours.txt      person-hours estimate and method
    actual-hours/            day-by-day hours for each team member
    meeting-notes/           weekly meeting notes
    project1/                documentation inherited from Group 2
README.md                    this file
```

---

## Authors and attribution

**Project 2 (Group 1):** Drew Medlock, Kyler Russell, Luke Reicherter, Alex Rawson, Blake Pennel, Carter Steenhard, Kyle Fleming

**Original Project 1 (Group 2):** Parker Albright, Aidan Atwood, Joseph Wen H Tan, Ever Armenta, Atique Ahanaf Danial, Viren Chowdary Padarthi ([original repository](https://github.com/VirenPadarthi/EECS-581-Project-1-Group-2))

Parts of the code and documentation were written with the help of generative AI (Claude Opus 5.5 and OpenAI Codex). Each such section is marked in the source's file header and in-code comments with its author and the tool used.
