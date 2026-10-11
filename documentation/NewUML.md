<!--
# Course: EECS 581: Software Engineering II
# Project: Minesweeper
# Description: System architecture and UML diagrams of the module, tile class,
#              game states, AI turns and custom timer/leaderboard feature.
#              Based on main at commit c9504510565278e184dbc941f866d0328342ab66.
# Inputs:
#     Current minesweeper.py source, module state and event handling.
# Outputs:
#     Architecture overview and UML structure, state and sequence diagrams.
# Author: Carter Steenhard
# Source attribution: Original project documentation created with the assistance
#                     of OpenAI Codex, describing the existing source implementation.
# Date: 10/11/2026
-->

# NewUML

Source: [`EECS-581-Project-1-Group-2/minesweeper.py`](../EECS-581-Project-1-Group-2/minesweeper.py).
These Mermaid diagrams render directly on GitHub.

<!--
# ---------------------------------------------------------------------------
# System architecture overview
#
# Boxes group responsibilities inside the existing minesweeper.py module.
# Arrows show input, shared state, rendering and persisted leaderboard data.
# These are logical components, not additional Python classes or files.
# ---------------------------------------------------------------------------
-->

## System architecture overview

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
    Rendering -->|graphical display| Player
```

The main loop routes input to the active screen and redraws it at up to 60 frames
per second. Player and AI reveals use the same move helpers and the same
`board[y][x]` tile objects. Interactive AI replies use a one-shot Pygame timer;
automatic AI uses a repeating timer. The game-duration timer separately measures
elapsed Pygame ticks. Restart replaces the board and clears game/timer state,
while saved leaderboard entries remain available.

For future extensions, add AI strategies through `do_AI_action()` and the shared
move helpers, add display information through the drawing functions, and preserve
the leaderboard entry fields when changing persistence. The existing function
groups below identify where each responsibility is implemented.

<!--
# ---------------------------------------------------------------------------
# Module and tile structure
#
# Tile is the only application class. The other boxes describe the existing
# module, external libraries and files; they do not represent new game classes.
# Module members shown here are the main state variables and entry points.
# ---------------------------------------------------------------------------
-->

## Module and tile structure

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
        start_game()
        reset_game()
        open_tile(tile)
        flag_tile(tile)
        handle_ai_event()
        do_AI_action()
        handle_win()
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

`board` contains 10 rows of 10 tiles. `reset_game()` replaces all tiles.
Tile states are `-1` covered, `-2` flagged, `-3` revealed bomb, `0` blank,
and `1` through `8` the number of neighboring bombs. First-click placement
excludes the clicked tile and all its neighbors. The selected mine count is 10–20.
`leaderboard.json` is created at runtime beside `minesweeper.py`; each entry is a
dictionary, and each mine count retains its fastest 10 times.

### Module function groups

All functions below are defined directly in `minesweeper.py`. These groups follow
the source's sections and explain the responsibilities behind the diagram.

| Responsibility | Existing functions |
| --- | --- |
| Board creation, lookup and reveal | `set_bombs`, `getTile`, `reveal_tile`, `reveal_bombs`, `check_win`, `flag_bombs`, `reset_game`, `set_tile_state`, `is_valid_index` |
| Shared player and AI moves | `neighbors`, `hidden_tiles`, `random_hidden_tile`, `open_tile`, `flag_tile` |
| Game timer | `start_timer`, `stop_timer`, `elapsed_seconds` |
| AI selection and timing | `set_bot_type`, `start_ai_timer`, `stop_ai_timer`, `schedule_ai_turn`, `handle_ai_event`, `do_AI_action` |
| AI strategies | `easy_AI_action`, `apply_basic_rules`, `medium_AI_action`, `apply_121_rule`, `hard_AI_action` |
| Selection screen | `parse_mine_count`, `draw_button`, `draw_option_row`, `drawSelection`, `handle_selection_event`, `start_game` |
| Board and text rendering | `drawBoard`, `draw_game_status`, `draw_text_centered`, `draw_text_aligned` |
| Leaderboard and name entry | `keep_top_times`, `times_for_mines`, `load_leaderboard`, `save_leaderboard`, `qualifies_for_leaderboard`, `add_leaderboard_entry`, `handle_win`, `open_leaderboard`, `drawNameEntry`, `handle_name_entry_event`, `drawLeaderboard`, `handle_leaderboard_event` |
| Controls help box | `open_info`, `close_info`, `info_lines`, `drawInfo`, `handle_info_event` |
| Legacy bomb helpers | `can_place_bomb`, `get_rand_chance` (not used by the current `set_bombs` placement path) |

<!--
# ---------------------------------------------------------------------------
# Custom addition: game timer and local leaderboard
#
# This UML sequence describes the implemented custom feature: measuring game
# duration and saving the fastest eligible manual wins for each mine count.
# It includes losses, AI-assisted wins, nonqualifying times and skipped names.
# ---------------------------------------------------------------------------
-->

## Custom addition: game timer and local leaderboard

The custom feature measures game duration and stores the fastest manual wins.
Timing starts on the first reveal, ends on a win or loss, and displays a fixed
final time after the game ends. A qualifying manual win prompts for a name and
saves a ranked entry for that game's mine count.

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

Each entry contains `name` (string), `time` (seconds), and `mines` (integer).
`keep_top_times()` retains at most 10 entries for each mine count, with lower
times first and earlier entries ahead when times tie. A full ranking requires
a strictly faster time to qualify. Games started in an AI mode or assisted
through `E` are excluded. The `L` key and menu leaderboard button let the player
view existing results without adding a score; Left/Right selects the mine count.

The timer continues measuring elapsed ticks while a leaderboard overlay is open
during an unfinished game. Closing that overlay resumes the existing board.
Restart resets timing but keeps the stored leaderboard.

<!--
# ---------------------------------------------------------------------------
# Game and screen states
#
# States summarize the main loop's flags. Leaderboard and name entry are
# overlays; closing the leaderboard returns to the screen underneath it.
# ---------------------------------------------------------------------------
-->

## Game and screen states

```mermaid
stateDiagram-v2
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
    Game --> Info : ? button, I or ? key / open_info()
    Info --> Game : any key or click / close_info(); same board
    Won --> NameEntry : no AI used and time qualifies
    NameEntry --> Leaderboard : Enter / add_leaderboard_entry(), open_leaderboard()
    NameEntry --> Won : Esc / skip saving
    Selection --> Leaderboard : leaderboard button
    Game --> Leaderboard : L / open_leaderboard()
    Leaderboard --> Leaderboard : Left or Right / change mine count
    Leaderboard --> ReturnScreen : other key or mouse click / close overlay
    state ReturnScreen <<choice>>
    ReturnScreen --> Selection : in_selection
    ReturnScreen --> Game : game screen underneath; keep existing board and flags
```

The main loop processes name entry or leaderboard events before selection and game
events. Those overlays suspend game-event processing. A win without a qualifying
manual time stays on the won board. Closing an overlay keeps the underlying game
state; it does not reset the board. Window-close events call `pygame.quit()` and
`sys.exit()` from any screen.

The game draws elapsed time, remaining mines (`max_num_of_bombs` minus flags),
and status every frame. Remaining mines can be negative when too many flags are
placed. Status distinguishes victory, loss, manual play, interactive AI,
automatic AI and paused automatic AI.

<!--
# ---------------------------------------------------------------------------
# Interactive AI turn
#
# Player reveals and AI reveals use open_tile(). A player flag change also
# schedules an interactive reply. Automatic mode uses a repeating timer.
# ---------------------------------------------------------------------------
-->

## Interactive AI turn

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

One AI turn can flag or reveal several tiles when a deduction applies. All AI
reveals use the same bomb placement, flood fill, timer, win and loss handling
as player reveals. Basic rules flag known mines or reveal neighbors once all
adjacent mines are flagged. Hard mode also checks horizontal and vertical 1-2-1
patterns whose covered neighbors lie on a single side.

Automatic mode starts a repeating 1000 ms timer in `reset_game()`. The `E` key
toggles repeating AI play and selects easy difficulty if none was selected.
Restarting cancels queued AI events and restarts the timer only for automatic
mode. Games started in either AI mode, or assisted through `E`, are excluded
from the leaderboard.
