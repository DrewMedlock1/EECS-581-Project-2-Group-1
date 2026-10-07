# Names: Parker Albright, Aidan Atwood, Joseph Wen H Tan, Ever Armenta, Atique Ahanaf Danial, Viren Chowdary Padarthi
# Project 2 Authors: Drew Medlock
# Course: EECS 581: Software Engineering II
# Project: Minesweeper
# Description: This program creates a 10 x 10 board and randomly populates the spaces with bombs. The goal
#              is to clear all safe spaces without tripping a bomb. A space will become blank on click or
#              show a number indicating how many bombs are touching the space.
# Changes made to Original:
#       Fixes:
#
#       Features:
#           Resize the game window - Drew Medlock
#               - Used Pygame documentation: https://www.pygame.org/docs/ref/display.html
#           Guarantee 0 mines around first click - Drew Medlock
#           Added Menu screen to select difficulty and number of mines - Kyler Russell 10/6/2026
#           Added game timer and local leaderboard of fastest win times - Luke Reicherter 10/6/2026
#               - Created with the assistance of Claude (Opus 5.5)
#       AI Modes added:
#           Easy mode - Drew Medlock
# Date: 9/19/2026

import pygame
import sys
import random
import json  # Used to save the leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
from pathlib import Path

pygame.init()

# Save the settings related to the layout of our board

boardSize = 10
tileSize = 17

boardX = 25
boardY = 25

# controls difficulty and number of boms
## can change number of bombs, will always have this many bombs
max_num_of_bombs = 10
per_chance_bomb = 0.10 # weighted percent chance that a tile has a bomb

boardWidth = boardSize * tileSize
boardHeight = boardSize * tileSize

windowWidth = boardX + boardWidth + 10
windowHeight = boardY + boardHeight + 30

screen = pygame.display.set_mode((windowWidth, windowHeight), pygame.SCALED | pygame.RESIZABLE)
                                                                  # Set the window to be both scalable and resizeable
pygame.display.set_caption("Minesweeper")

clock = pygame.time.Clock()

# Save a few basic colors

white = (255, 255, 255)
black = (0, 0, 0)


# Save the images we'll reference for graphics

## Directory paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Font used for text in the window
font = pygame.font.Font(ASSETS_DIR / "Minesweeper.ttf", 10) # Update to use a minesweeper font that looks better at
                                                                 # different scales - Drew Medlock

coveredTile = pygame.image.load(ASSETS_DIR / "block.png")
selectedTile = pygame.image.load(ASSETS_DIR / "selblock.png")
blankTile = pygame.image.load(ASSETS_DIR / "blankblock.png")
flagImage = pygame.image.load(ASSETS_DIR / "flag.png")
bombImage = pygame.image.load(ASSETS_DIR / "bomb.png")

numbers = {
    1: pygame.image.load(ASSETS_DIR / "block1.png"),
    2: pygame.image.load(ASSETS_DIR / "block2.png"),
    3: pygame.image.load(ASSETS_DIR / "block3.png"),
    4: pygame.image.load(ASSETS_DIR / "block4.png"),
    5: pygame.image.load(ASSETS_DIR / "block5.png"),
    6: pygame.image.load(ASSETS_DIR / "block6.png"),
    7: pygame.image.load(ASSETS_DIR / "block7.png"),
    8: pygame.image.load(ASSETS_DIR / "block8.png")
}

# ---------------------------------------------------------------------------
# Create a class for our tiles
#
# State descriptions:
# -1 = the tile is still "covered"
# -2 = the tile has a flag on it
# -3 = the tile was clicked and has a bomb
# 0 = the tile has been clicked on and is revealed blank
# 1-8 = the tile has been clicked on and is revealed to have a number on it
# ---------------------------------------------------------------------------

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(
            boardX + x * tileSize,
            boardY + y * tileSize,
            tileSize,
            tileSize
        )

        self.state = -1
        self.has_bomb = False

# Create the board

board = [ [Tile(x, y) for x in range(boardSize)] for y in range(boardSize) ]

# Sets bombs on the board
# iterates through board
# if can_place bomb
# place bomb
# display in console where the bombs arelocated

# I changed the bomb placing logic to be a little more random.
# Added first click is always safe - Joseph
def set_bombs(board, safe_tile):
    candidates = [tile for row in board for tile in row if tile is not safe_tile]
    # Drew Medlock - Remove neighbors from the first selection to give an easier start
    for row in range(safe_tile.y - 1, safe_tile.y + 2):
        for col in range(safe_tile.x - 1, safe_tile.x + 2):
            if 0 <= row < boardSize and 0 <= col < boardSize and (col, row) != (safe_tile.x, safe_tile.y):
                candidates.remove(board[row][col])
    for tile in random.sample(candidates, max_num_of_bombs):
        tile.has_bomb = True
        print("placed bomb at ", tile.x, " ", tile.y)
         
# Helper function
# determines if a bomb can be placed on a given tile
# checks if tile has bomb, continue
# generates random chance to place bomb, place bomb
## expand logic to not let player lose on first click later

def can_place_bomb(tile, curr_bombs) -> bool:
    if not tile.has_bomb:
        if get_rand_chance() <= per_chance_bomb:
            if curr_bombs < max_num_of_bombs:
                return True
    else:
        return False

# Helper function
# generates a random float between 0 and 1
## weighed against the percent chance variable above
### if roll below or equal to chance , place bomb
### else if roll above, no bomb

def get_rand_chance() -> float:
    return random.uniform(0.0, 1.0)

# Find what tile is under the mouse cursor

def getTile(mousePos):
    for row in board:
        for tile in row:
            if tile.rect.collidepoint(mousePos):
                return tile

    return None

# Reveals a tile, and if it has no neighboring bombs, keeps
# revealing its neighbors too (flood fill)
def reveal_tile(start_tile):
    stack = [start_tile]

    while stack:
        tile = stack.pop()
        # Skip anything that isn't covered (flagged or already revealed)
        if tile.state != -1:
            continue

        set_tile_state(tile)

        # Blank tile: queue up all 8 neighbors to be revealed too
        if tile.state == 0:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx = tile.x + dx
                    ny = tile.y + dy

                    if is_valid_index(nx, ny):
                        stack.append(board[ny][nx])

# Shows every bomb that isn't already flagged,
# happens when the player loses
def reveal_bombs():
    for row in board:
        for tile in row:
            if tile.has_bomb and tile.state != -2:
                tile.state = -3

# True when every tile without a bomb has been revealed
def check_win():
    for row in board:
        for tile in row:
            if not tile.has_bomb and tile.state < 0:
                return False
    return True

#Flags every bomb, used when the player wins
def flag_bombs():
    for row in board:
        for tile in row:
            if tile.has_bomb:
                tile.state = -2

# Game timer - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
# The timer starts on the first reveal (when the bombs are placed) and stops when the game is won or lost
def start_timer():
    global game_start_ticks
    game_start_ticks = pygame.time.get_ticks()

def stop_timer():
    global final_time
    final_time = elapsed_seconds()

def elapsed_seconds() -> float:
    if game_start_ticks is None:
        return 0.0
    if final_time is not None:
        return final_time
    return (pygame.time.get_ticks() - game_start_ticks) / 1000

# Builds a fresh board with new bombs and clears the loss state
def reset_game():
    global board, game_over, game_won, bombs_placed, AI_on, game_start_ticks, final_time, ai_used
    board = [
        [Tile(x, y) for x in range(boardSize)]
        for y in range(boardSize)
    ]
    game_over = False
    game_won = False
    bombs_placed = False
    AI_on = False
    # Reset the timer and AI tracking for the leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    game_start_ticks = None
    final_time = None
    # Games where the AI made moves are not eligible for the leaderboard
    ai_used = AI_mode != 'manual'

# Sets tile state to number of bombs surrounding
# iterates through all tiles around clicked tile
# if detects a bomb, increases tile state by 1
# uses code in main loop to display tile state

# I changed 2 things.
# 1. board[ny][nx] instead of board [x][y] since the board is built as rows first.
# 2. No more board_grid_x += 1 inside the loop. Instead of moving the starting corner,
# the offsets dx and dy are added to the tile's position on every check, so the scan always
# covers the same 3x3 area - Joseph
def set_tile_state(tile):
    count = 0

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx = tile.x + dx
            ny = tile.y + dy

            print("checking[", nx, ",", ny, "]")

            if is_valid_index(nx, ny):
                if board[ny][nx].has_bomb:
                    count += 1

                    print("Setting tilestate to: ", count)
    tile.state = count

# helper function
# boolean function that determines if an index is valid or not

def is_valid_index(x, y) -> bool:
    if x >= boardSize or y >= boardSize:
        return False
    if x < 0 or y < 0:
        return False
            
    return True

# Draw the board for the user

# Easy bot that will click on not flagged, and not revealed tiles - Drew Medlock
def toggle_bot():
    """
    This toggles a global AI on vs AI off state to set the timer for 1 second AI moves
    """
    global AI_on
    if AI_on:
        AI_on = False
        return
    else:
        AI_on = True

def set_bot_type(bot_type):
    """
    This sets a global value for the bot type that is currently being used in the AI action
    """
    global AI_type
    AI_type = bot_type

def do_AI_action():
    """
    Dispatcher function based on assigned AI type to correct level of AI
    """
    if AI_type == 'easy':
        easy_AI_action()

def easy_AI_action():
    """
    Randomly chooses a tile to attempt to reveal it, if it is already revealed or is flagged it picks another
    """
    # Added game_won to the globals and stop on a win so a won game no longer loops forever,
    # and start / stop the timer - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    global game_over, game_won, bombs_placed
    revealed_tile = False
    while not revealed_tile:
        if game_over or game_won:
            break
        x = random.randint(0, boardSize - 1)
        y = random.randint(0, boardSize - 1)
        tile = board[x][y]
        if tile.state == -1:
            if not bombs_placed:
                set_bombs(board, tile)
                bombs_placed = True
                start_timer()
                revealed_tile = True

            if tile.has_bomb:
                tile.state = -3
                reveal_bombs()
                revealed_tile = True
                game_over = True
                stop_timer()
            else:
                reveal_tile(tile)
                revealed_tile = True
                if check_win():
                    flag_bombs()
                    game_won = True
                    stop_timer()

def drawBoard(mouseTile):
    screen.fill(white)

    # Draw column labels from A - J on top of the board
    for x in range(boardSize):
        label = font.render(
            chr(ord('A') + x),
            True,
            black
        )

        labelRect = label.get_rect(
            center=(
                boardX + x * tileSize + tileSize // 2,
                boardY // 2
            )
        )
        screen.blit(label, labelRect)

    # Draw row labels from 1 - 10 on the left of the board
    for y in range(boardSize):
        label = font.render(
            str(y + 1),
            True,
            black
        )

        labelRect = label.get_rect(
            center=(
                boardX // 2,
                boardY + y * tileSize + tileSize // 2
            )
        )
        screen.blit(label, labelRect)

    for row in board:
        for tile in row:
            if tile.state == -1:
                if tile == mouseTile:
                    screen.blit(selectedTile, tile.rect)
                else:
                    screen.blit(coveredTile, tile.rect)

            elif tile.state == -2:
                screen.blit(flagImage, tile.rect)

            elif tile.state == -3:
                screen.blit(bombImage, tile.rect)

            elif tile.state == 0:
                screen.blit(blankTile, tile.rect)

            elif tile.state in numbers:
                screen.blit(
                    numbers[tile.state],
                    tile.rect
                )

# ---------------------------------------------------------------------------
# Game setup selection screen (number of mines + AI settings)
#
# The selection screen only records the player's choices in flags. When
# "Start Game" is pressed, start_game() copies them into the flags used by
# the game itself:
#   max_num_of_bombs - number of mines placed on the board (10-20)
#   AI_mode          - 'manual', 'interactive', or 'automatic'
#   AI_difficulty    - 'easy', 'medium', or 'hard' ('' when AI_mode is 'manual')
#   AI_type          - same as AI_difficulty, read by do_AI_action()
# The AI behavior for each mode/difficulty still needs to be implemented.
# Used Opus 5.5 to code this, given the instructions to Complete the sections 
# in the code which describe adding the selection for the AI and number of mines. 
# the code was then tested by Kyler Russell.
# ---------------------------------------------------------------------------

MIN_MINES = 10
MAX_MINES = 20

AI_MODES = ['manual', 'interactive', 'automatic']
AI_MODE_LABELS = {
    'manual': 'Manual',
    'interactive': 'Interactive',
    'automatic': 'Automatic'
}
AI_MODE_DESCRIPTIONS = {
    'manual': 'No AI',
    'interactive': 'You and the AI alternate turns',
    'automatic': 'AI plays until it loses'
}
AI_DIFFICULTIES = ['easy', 'medium', 'hard']
AI_DIFFICULTY_LABELS = {
    'easy': 'Easy',
    'medium': 'Medium',
    'hard': 'Hard'
}

# Colors used by the selection screen
gray = (192, 192, 192)
light_gray = (225, 225, 225)
dark_gray = (90, 90, 90)
red = (200, 0, 0)
green = (0, 150, 0)

# Choices currently shown on the selection screen
in_selection = True                     # True while the selection screen is showing
mine_input_text = str(max_num_of_bombs) # Text typed into the mine count box
mine_input_active = True                # True when the mine count box accepts typing
selected_AI_mode = 'manual'
selected_AI_difficulty = 'easy'

# Settings for the game being played, set by start_game()
AI_mode = 'manual'
AI_difficulty = ''

# Clickable areas on the selection screen, filled in by drawSelection()
selection_rects = {}
selection_mouse_pos = (0, 0)

def parse_mine_count():
    """
    Returns the number typed into the mine count box, or None if it is not a whole number from 10-20
    """
    if not mine_input_text.isdigit():
        return None
    count = int(mine_input_text)
    if MIN_MINES <= count <= MAX_MINES:
        return count
    return None

def draw_text_centered(text, color, center):
    """
    Draws a line of text centered on the given point
    """
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))

def draw_button(rect, text, selected=False, enabled=True):
    """
    Draws a selectable button. Selected buttons are filled dark, and buttons under the mouse are highlighted
    """
    if not enabled:
        fill, text_color = light_gray, gray
    elif selected:
        fill, text_color = dark_gray, white
    elif rect.collidepoint(selection_mouse_pos):
        fill, text_color = light_gray, black
    else:
        fill, text_color = gray, black

    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, black, rect, 1)
    draw_text_centered(text, text_color, rect.center)

def draw_option_row(options, labels, selected, top, key_prefix):
    """
    Draws a row of equally sized buttons, one per option, and saves their rects for click detection
    """
    margin = 7
    gap = 3
    width = (windowWidth - 2 * margin - gap * (len(options) - 1)) // len(options)
    for i, option in enumerate(options):
        rect = pygame.Rect(margin + i * (width + gap), top, width, 18)
        draw_button(rect, labels[option], selected=(option == selected))
        selection_rects[key_prefix + option] = rect

def drawSelection():
    """
    This draws a box which displays a header which says enter the number of mines 10-20
    Then beneath this is a box which allows the user to enter a number from 10-20
    Beneath this is another header saying select the AI type, with the options being
    manual (no AI), interactive (alternate turns), and automatic (AI plays until loss)
    If any of the AI settings are chosen, there should be sub-options which show up beneath
    with a header saying select AI difficulty / skill (easy, medium, hard)
    At the bottom of the box there should be a button that says start game that will start the game
    """
    selection_rects.clear()
    screen.fill(white)

    # Outer box around the whole selection screen
    pygame.draw.rect(screen, black, pygame.Rect(4, 4, windowWidth - 8, windowHeight - 8), 1)

    center_x = windowWidth // 2
    mine_count = parse_mine_count()

    # Mine count header, turns red while the typed value is not valid
    draw_text_centered(
        "Number of mines (" + str(MIN_MINES) + "-" + str(MAX_MINES) + ")",
        black if mine_count is not None else red,
        (center_x, 16)
    )

    # Mine count input box
    input_rect = pygame.Rect(center_x - 25, 26, 50, 18)
    pygame.draw.rect(screen, white, input_rect)
    pygame.draw.rect(screen, dark_gray if mine_input_active else gray, input_rect, 2 if mine_input_active else 1)
    input_display = mine_input_text
    if mine_input_active and (pygame.time.get_ticks() // 500) % 2 == 0:
        input_display += "|"    # Blinking cursor
    draw_text_centered(input_display, black, input_rect.center)
    selection_rects['mine_input'] = input_rect

    # AI type header, options, and a description of the chosen option
    draw_text_centered("Select AI type", black, (center_x, 58))
    draw_option_row(AI_MODES, AI_MODE_LABELS, selected_AI_mode, 66, 'mode_')
    draw_text_centered(AI_MODE_DESCRIPTIONS[selected_AI_mode], dark_gray, (center_x, 94))

    # AI difficulty sub-options, only shown when an AI mode is chosen
    if selected_AI_mode != 'manual':
        draw_text_centered("Select AI difficulty", black, (center_x, 116))
        draw_option_row(AI_DIFFICULTIES, AI_DIFFICULTY_LABELS, selected_AI_difficulty, 124, 'difficulty_')

    # Leaderboard button above the start button - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    leaderboard_rect = pygame.Rect(center_x - 45, windowHeight - 62, 90, 20)
    draw_button(leaderboard_rect, "Leaderboard")
    selection_rects['leaderboard'] = leaderboard_rect

    # Start game button at the bottom of the box, disabled until the mine count is valid
    start_rect = pygame.Rect(center_x - 45, windowHeight - 36, 90, 22)
    draw_button(start_rect, "Start Game", enabled=(mine_count is not None))
    selection_rects['start'] = start_rect

def handle_selection_event(event):
    """
    Handles mouse and keyboard input while the selection screen is showing
    """
    global mine_input_text, mine_input_active, selected_AI_mode, selected_AI_difficulty, selection_mouse_pos

    if event.type == pygame.MOUSEMOTION:
        selection_mouse_pos = event.pos

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # The mine count box only accepts typing after it is clicked
        mine_input_active = selection_rects.get('mine_input', pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos)

        for key, rect in selection_rects.items():
            if not rect.collidepoint(event.pos):
                continue
            if key.startswith('mode_'):
                selected_AI_mode = key[len('mode_'):]
            elif key.startswith('difficulty_'):
                selected_AI_difficulty = key[len('difficulty_'):]
            elif key == 'start' and parse_mine_count() is not None:
                start_game()
            # Open the leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
            elif key == 'leaderboard':
                # Show the mine count typed in the box, or the last game's if the box isn't valid
                open_leaderboard(parse_mine_count() or max_num_of_bombs)

    elif event.type == pygame.KEYDOWN:
        # Enter starts the game from anywhere on the selection screen
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if parse_mine_count() is not None:
                start_game()
            return

        if not mine_input_active:
            return

        if event.key == pygame.K_BACKSPACE:
            mine_input_text = mine_input_text[:-1]

        # Up / down arrows step the mine count within 10-20
        elif event.key in (pygame.K_UP, pygame.K_DOWN):
            step = 1 if event.key == pygame.K_UP else -1
            current = int(mine_input_text) if mine_input_text.isdigit() else MIN_MINES - step
            mine_input_text = str(max(MIN_MINES, min(MAX_MINES, current + step)))

        # Only accept digits, at most 2 characters
        elif event.unicode.isdigit() and len(mine_input_text) < 2:
            mine_input_text += event.unicode

def start_game():
    """
    Applies the choices from the selection screen to the game flags and starts a fresh board
    """
    global in_selection, max_num_of_bombs, AI_mode, AI_difficulty

    max_num_of_bombs = parse_mine_count()

    AI_mode = selected_AI_mode
    AI_difficulty = selected_AI_difficulty if AI_mode != 'manual' else ''
    set_bot_type(AI_difficulty)

    # reset_game() moved after the AI settings so it knows whether the AI is playing - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    reset_game()

    # TODO: Start the chosen AI here once it is implemented, e.g.
    #   'interactive' - let the AI take a move after each player move
    #   'automatic'   - toggle_bot() and pygame.time.set_timer(AI_event, 1000)

    in_selection = False
    print("Starting game with", max_num_of_bombs, "mines, AI mode:", AI_mode, "AI difficulty:", AI_difficulty)

# ---------------------------------------------------------------------------
# Local leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
#
# Keeps the fastest win times (in seconds) in leaderboard.json next to this
# file. Each mine count (10-20) has its own top LEADERBOARD_SIZE, so a win
# is only compared against games played with the same number of mines.
# Lower times rank higher; ties keep the earlier entry ahead. Only games
# won without any AI moves are eligible. When a win makes the top times for
# its mine count, the player is asked for a name before it is saved.
#   leaderboard         - every saved entry, sorted fastest first
#   entering_name       - True while the name entry screen is showing
#   showing_leaderboard - True while the leaderboard screen is showing
#   leaderboard_mines   - mine count of the leaderboard being shown
#   highlight_index     - row of the newest entry to highlight, or None
# ---------------------------------------------------------------------------

LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"
LEADERBOARD_SIZE = 10
NAME_MAX_LENGTH = 8

entering_name = False
name_input_text = ""
showing_leaderboard = False
leaderboard_mines = MIN_MINES
highlight_index = None

def keep_top_times(entries):
    """
    Sorts entries fastest first and keeps only the top LEADERBOARD_SIZE for each mine count
    """
    entries.sort(key=lambda e: e['time'])  # Stable sort keeps earlier ties ahead
    kept = []
    counts = {}
    for entry in entries:
        counts[entry['mines']] = counts.get(entry['mines'], 0) + 1
        if counts[entry['mines']] <= LEADERBOARD_SIZE:
            kept.append(entry)
    return kept

def times_for_mines(mines):
    """
    Returns the ranked times for one mine count
    """
    return [entry for entry in leaderboard if entry['mines'] == mines]

def load_leaderboard():
    """
    Reads the saved leaderboard, returning an empty one if the file is missing or unreadable
    """
    try:
        data = json.loads(LEADERBOARD_FILE.read_text())
    except (OSError, ValueError):
        return []

    entries = []
    for entry in data if isinstance(data, list) else []:
        try:
            entries.append({
                'name': str(entry['name']),
                'time': float(entry['time']),
                'mines': int(entry['mines'])
            })
        except (KeyError, TypeError, ValueError):
            continue    # Skip malformed entries instead of losing the whole file
    return keep_top_times(entries)

def save_leaderboard():
    try:
        LEADERBOARD_FILE.write_text(json.dumps(leaderboard, indent=2))
    except OSError as error:
        print("Could not save leaderboard:", error)

def qualifies_for_leaderboard(seconds, mines) -> bool:
    times = times_for_mines(mines)
    return len(times) < LEADERBOARD_SIZE or seconds < times[-1]['time']

def add_leaderboard_entry(name, seconds, mines):
    """
    Inserts a new time, trims its mine count's leaderboard to the max size, saves it, and returns the new entry's row
    """
    global leaderboard
    entry = {'name': name, 'time': round(seconds, 2), 'mines': mines}
    leaderboard.append(entry)
    leaderboard = keep_top_times(leaderboard)
    save_leaderboard()
    return next((i for i, e in enumerate(times_for_mines(mines)) if e is entry), None)

def handle_win():
    """
    Called when the player wins: stops the timer and asks for a name if the time makes the leaderboard
    """
    global entering_name, name_input_text
    stop_timer()
    if not ai_used and qualifies_for_leaderboard(final_time, max_num_of_bombs):
        entering_name = True
        name_input_text = ""

def open_leaderboard(mines, highlight=None):
    """
    Shows the leaderboard for the given mine count, optionally highlighting one row
    """
    global showing_leaderboard, leaderboard_mines, highlight_index
    showing_leaderboard = True
    leaderboard_mines = mines
    highlight_index = highlight

def drawNameEntry():
    """
    Shows the winning time and a box for the player to type their name
    """
    screen.fill(white)
    pygame.draw.rect(screen, black, pygame.Rect(4, 4, windowWidth - 8, windowHeight - 8), 1)
    center_x = windowWidth // 2

    draw_text_centered("You win!", green, (center_x, 30))
    draw_text_centered("Time: " + format(final_time, ".2f") + "s", black, (center_x, 48))
    draw_text_centered("Top " + str(LEADERBOARD_SIZE) + " for " + str(max_num_of_bombs) + " mines!", black, (center_x, 66))
    draw_text_centered("Enter your name", black, (center_x, 96))

    input_rect = pygame.Rect(center_x - 45, 106, 90, 18)
    pygame.draw.rect(screen, white, input_rect)
    pygame.draw.rect(screen, dark_gray, input_rect, 2)
    input_display = name_input_text
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        input_display += "|"    # Blinking cursor
    draw_text_centered(input_display, black, input_rect.center)

    draw_text_centered("Enter = save", dark_gray, (center_x, windowHeight - 40))
    draw_text_centered("Esc = skip", dark_gray, (center_x, windowHeight - 24))

def handle_name_entry_event(event):
    global entering_name, name_input_text
    if event.type != pygame.KEYDOWN:
        return

    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        name = name_input_text.strip() or "Player"
        row = add_leaderboard_entry(name, final_time, max_num_of_bombs)
        entering_name = False
        open_leaderboard(max_num_of_bombs, row)

    elif event.key == pygame.K_ESCAPE:
        entering_name = False

    elif event.key == pygame.K_BACKSPACE:
        name_input_text = name_input_text[:-1]

    # Only accept letters, digits, and spaces so the name fits on the leaderboard
    elif (event.unicode.isalnum() or event.unicode == " ") and len(name_input_text) < NAME_MAX_LENGTH:
        name_input_text += event.unicode

def draw_text_aligned(text, color, pos, align):
    """
    Draws a line of text anchored at pos, with align being 'midleft' or 'midright'
    """
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(**{align: pos}))

def drawLeaderboard():
    """
    Draws the top times for the selected mine count as rows of rank, name, and time in seconds
    """
    screen.fill(white)
    pygame.draw.rect(screen, black, pygame.Rect(4, 4, windowWidth - 8, windowHeight - 8), 1)
    center_x = windowWidth // 2

    # Column anchors: rank and time are right aligned, name is left aligned
    rank_x = 24
    name_x = 30
    time_x = windowWidth - 14

    draw_text_centered("Leaderboard", black, (center_x, 14))

    # Mine count being shown, with arrows when there is another mine count to switch to
    left_arrow = "< " if leaderboard_mines > MIN_MINES else "  "
    right_arrow = " >" if leaderboard_mines < MAX_MINES else "  "
    draw_text_centered(left_arrow + str(leaderboard_mines) + " mines" + right_arrow, black, (center_x, 28))

    header_y = 42
    draw_text_aligned("Name", dark_gray, (name_x, header_y), 'midleft')
    draw_text_aligned("Secs", dark_gray, (time_x, header_y), 'midright')

    times = times_for_mines(leaderboard_mines)
    if not times:
        draw_text_centered("No times yet", dark_gray, (center_x, 100))

    for i, entry in enumerate(times):
        y = header_y + 14 + i * 13
        color = green if i == highlight_index else black
        draw_text_aligned(str(i + 1) + ".", color, (rank_x, y), 'midright')
        draw_text_aligned(entry['name'], color, (name_x, y), 'midleft')
        draw_text_aligned(format(entry['time'], ".2f"), color, (time_x, y), 'midright')

    draw_text_centered("Left / Right = mines", dark_gray, (center_x, windowHeight - 28))
    draw_text_centered("Other keys = back", dark_gray, (center_x, windowHeight - 15))

def handle_leaderboard_event(event):
    """
    Left / right arrows switch mine counts. Any other key press or a click closes the leaderboard
    and returns to the previous screen
    """
    global showing_leaderboard, leaderboard_mines, highlight_index
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
        step = 1 if event.key == pygame.K_RIGHT else -1
        new_mines = max(MIN_MINES, min(MAX_MINES, leaderboard_mines + step))
        if new_mines != leaderboard_mines:
            leaderboard_mines = new_mines
            highlight_index = None  # The highlighted entry belongs to the previous mine count

    elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONUP):
        showing_leaderboard = False
        highlight_index = None

leaderboard = load_leaderboard()

# ----------
# Main loop
# ----------

mouseTile = None
game_over = False
game_won = False
bombs_placed = False
AI_on = False
AI_type = ''
# Timer and leaderboard state - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
game_start_ticks = None
final_time = None
ai_used = False

AI_event = pygame.USEREVENT + 1

while True:
    # Name entry and leaderboard screens draw over both the selection screen and the game
    # Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    if entering_name or showing_leaderboard:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if entering_name:
                handle_name_entry_event(event)
            else:
                handle_leaderboard_event(event)

        if entering_name:
            drawNameEntry()
        else:
            drawLeaderboard()
        pygame.display.flip()
        clock.tick(60)
        continue

    # Draw selection box for the AI and number of mines
    if in_selection:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            handle_selection_event(event)

        drawSelection()
        pygame.display.flip()
        clock.tick(60)
        continue

    # Catch-all event tracker
    for event in pygame.event.get():

        # Closes the game window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == AI_event:
            do_AI_action()

        # Keep track of which tile the mouse is currently over
        elif event.type == pygame.MOUSEMOTION:
            mouseTile = getTile(event.pos)

        # Restart with R
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()

            # Show the leaderboard with L - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
            elif event.key == pygame.K_l:
                open_leaderboard(max_num_of_bombs)

            # Added debug auto win for testing. Press tilde/backquote to flag every bomb
            ## Parker
            elif event.key == pygame.K_BACKQUOTE:
                for row in board:
                        for tile in row:
                            if tile.has_bomb:
                                tile.state = -2
            elif event.key == pygame.K_e:
                # Pressing 'e' toggles the easy mode bot on and off
                ai_used = True  # Bot-assisted games don't count for the leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
                if AI_on:
                    toggle_bot()
                    pygame.time.set_timer(AI_event, 0)
                else:
                    toggle_bot()
                    set_bot_type('easy')
                    pygame.time.set_timer(AI_event, 1000)

        # Check for mouse clicks, run if one is made
        elif event.type == pygame.MOUSEBUTTONUP:
            # Ignore all clicks once the game is lost
            if game_over:
                continue

            tile = getTile(event.pos)

            # Ignore mouse clicks that aren't on tiles
            if tile is None:
                continue

            # A left click on a covered tile reveals what's under it
            if event.button == 1:
                if tile.state == -1:
                    if not bombs_placed:
                        set_bombs(board, tile)
                        bombs_placed = True
                        start_timer()  # Luke Reicherter - created with the assistance of Claude (Opus 5.5)

                    if tile.has_bomb:
                        tile.state = -3
                        reveal_bombs()
                        game_over = True
                        stop_timer()  # Luke Reicherter - created with the assistance of Claude (Opus 5.5)
                    else:
                        reveal_tile(tile)

                        if check_win():
                            flag_bombs()
                            game_won = True
                            handle_win()  # Stops the timer and checks the leaderboard - Luke Reicherter - created with the assistance of Claude (Opus 5.5)

            # A right click adds or removes a flag
            elif event.button == 3:
                if tile.state == -1:
                    tile.state = -2

                elif tile.state == -2:
                    tile.state = -1

    drawBoard(mouseTile)

    # Timer under the board: whole seconds while playing, exact time once the game ends
    # Win / loss message moved down a line to make room - Luke Reicherter - created with the assistance of Claude (Opus 5.5)
    if final_time is not None:
        time_text = "Time: " + format(final_time, ".2f") + "s"
    else:
        time_text = "Time: " + str(int(elapsed_seconds())) + "s"
    draw_text_centered(time_text, black, (windowWidth // 2, boardY + boardHeight + 8))

    if game_over or game_won:
        if game_won:
            msg = font.render("You win! R = restart", True, (0, 150, 0))
        else:
            msg = font.render("You lost! R = restart", True, (200, 0, 0))

        screen.blit(
            msg,
            msg.get_rect(center=(windowWidth // 2, boardY + boardHeight + 21))
        )
    pygame.display.flip()
    clock.tick(60)
