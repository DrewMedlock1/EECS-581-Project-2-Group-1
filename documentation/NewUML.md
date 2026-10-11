<!--
# Course: EECS 581: Software Engineering II
# Project: Minesweeper
# Description: UML diagrams of the current module, tile class, game states and AI turns.
#              Based on main at commit 9b3d37a426c3ebd7c3cc82afbf9968925be48524.
# Inputs:
#     Current minesweeper.py source, module state and event handling.
# Outputs:
#     UML structure, state and sequence diagrams rendered with Mermaid.
# Created with the assistance of OpenAI Codex.
# Date: 10/11/2026
-->

# NewUML

Source: [`EECS-581-Project-1-Group-2/minesweeper.py`](../EECS-581-Project-1-Group-2/minesweeper.py).
These Mermaid diagrams render directly on GitHub.

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
| Legacy bomb helpers | `can_place_bomb`, `get_rand_chance` (not used by the current `set_bombs` placement path) |

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
