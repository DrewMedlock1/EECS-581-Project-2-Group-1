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
#       AI Modes added:
#           Easy mode - Drew Medlock
# Date: 9/19/2026

import pygame
import sys
import random
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

# Builds a fresh board with new bombs and clears the loss state
def reset_game():
    global board, game_over, game_won, bombs_placed, AI_on
    board = [
        [Tile(x, y) for x in range(boardSize)]
        for y in range(boardSize)
    ]
    game_over = False
    game_won = False
    bombs_placed = False
    AI_on = False

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
    global game_over, bombs_placed
    revealed_tile = False
    while not revealed_tile:
        if game_over:
            break
        x = random.randint(0, boardSize - 1)
        y = random.randint(0, boardSize - 1)
        tile = board[x][y]
        if tile.state == -1:
            if not bombs_placed:
                set_bombs(board, tile)
                bombs_placed = True
                revealed_tile = True

            if tile.has_bomb:
                tile.state = -3
                reveal_bombs()
                revealed_tile = True
                game_over = True
            else:
                reveal_tile(tile)
                revealed_tile = True
                if check_win():
                    flag_bombs()
                    game_won = True

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
# ----------
# Main loop
# ----------

mouseTile = None
game_over = False
game_won = False
bombs_placed = False
AI_on = False
AI_type = ''

AI_event = pygame.USEREVENT + 1

while True:

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
            
            # Added debug auto win for testing. Press tilde/backquote to flag every bomb
            ## Parker
            elif event.key == pygame.K_BACKQUOTE:
                for row in board:
                        for tile in row:
                            if tile.has_bomb:
                                tile.state = -2
            elif event.key == pygame.K_e:
                # Pressing 'e' toggles the easy mode bot on and off
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

                    if tile.has_bomb:
                        tile.state = -3
                        reveal_bombs()
                        game_over = True
                    else:
                        reveal_tile(tile)

                        if check_win():
                            flag_bombs()
                            game_won = True

            # A right click adds or removes a flag
            elif event.button == 3:
                if tile.state == -1:
                    tile.state = -2

                elif tile.state == -2:
                    tile.state = -1

    drawBoard(mouseTile)

    if game_over or game_won:
        if game_won:
            msg = font.render("You win! R = restart", True, (0, 150, 0))
        else:
            msg = font.render("You lost! R = restart", True, (200, 0, 0))

        screen.blit(
            msg,
            msg.get_rect(center=(windowWidth // 2, boardY + boardHeight + 15))
        )
    pygame.display.flip()
    clock.tick(60)
