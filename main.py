import pygame
import random
import time
from utils.sound import toggle_sound
from utils.leaderboard import load_scores, save_score

# Initialize Pygame and Pygame Mixer
pygame.init()
pygame.mixer.init()

# Set up display
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slider Puzzle")

# Load Sound Effect (Make sure the file path is correct)
try:
    move_sound = pygame.mixer.Sound("src/sounds/se.mp3")  
    completion_sound = pygame.mixer.Sound("src/sounds/cs.wav")  # Completion sound
except pygame.error as e:
    print(f"Error loading sound: {e}")

# Function to play the sound effect
def play_move_sound():
    if move_sound:
        move_sound.play()

def play_completion_sound():
    if completion_sound:
        completion_sound.play()

# Function to check if a tile can move (is adjacent to the empty space)
def is_adjacent(pos, empty_pos):
    return (abs(pos[0] - empty_pos[0]) == 1 and pos[1] == empty_pos[1]) or \
           (abs(pos[1] - empty_pos[1]) == 1 and pos[0] == empty_pos[0])

# Function to move a tile if adjacent to the empty space
def move_tile(grid, pos):
    global moves
    empty_pos = [(i, j) for i, row in enumerate(grid) for j, val in enumerate(row) if val is None][0]
    if is_adjacent(pos, empty_pos):
        # Swap tiles
        grid[empty_pos[0]][empty_pos[1]], grid[pos[0]][pos[1]] = grid[pos[0]][pos[1]], grid[empty_pos[0]][empty_pos[1]]
        moves += 1
        play_move_sound()  # Play sound effect when a tile is moved

# Function to count the number of inversions in the grid
def count_inversions(grid):
    """Count the number of inversions in the grid."""
    flat_grid = [tile for row in grid for tile in row if tile is not None]
    inversions = 0
    for i in range(len(flat_grid)):
        for j in range(i + 1, len(flat_grid)):
            if flat_grid[i] > flat_grid[j]:
                inversions += 1
    return inversions

# Function to check if the puzzle is solvable
def is_solvable(grid):
    """Check if the grid is solvable."""
    inversions = count_inversions(grid)
    empty_pos = find_empty_tile(grid)
    grid_size = len(grid)
    
    if grid_size % 2 == 1:  # Odd grid size
        return inversions % 2 == 0
    else:  # Even grid size
        # Blank is on an even row from the bottom (counting from 1)
        empty_row_from_bottom = grid_size - empty_pos[0]
        if empty_row_from_bottom % 2 == 0:
            return inversions % 2 == 1
        else:
            return inversions % 2 == 0

# Function to shuffle the grid using valid moves and ensure solvability
def shuffle_grid(grid, moves=100):
    empty_pos = find_empty_tile(grid)
    
    while True:
        for _ in range(moves):
            valid_moves = get_valid_moves(grid, empty_pos)
            next_move = random.choice(valid_moves)

            # Swap the empty tile with the selected valid move
            grid[empty_pos[0]][empty_pos[1]], grid[next_move[0]][next_move[1]] = \
                grid[next_move[0]][next_move[1]], grid[empty_pos[0]][empty_pos[1]]
            empty_pos = next_move  # Update the empty tile position
        
        if is_solvable(grid):
            break  # Only return the grid if it is solvable
    return grid

# Function to generate a solved grid
def generate_solved_grid(grid_size):
    grid = list(range(1, grid_size * grid_size)) + [None]  # None represents the empty space
    grid_2d = [grid[i * grid_size:(i + 1) * grid_size] for i in range(grid_size)]
    return grid_2d

# Function to find the position of the empty tile (None)
def find_empty_tile(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] is None:
                return i, j

# Function to get the valid moves for the empty tile (None)
def get_valid_moves(grid, empty_pos):
    valid_moves = []
    x, y = empty_pos
    if x > 0:  # Can move up
        valid_moves.append((x - 1, y))
    if x < len(grid) - 1:  # Can move down
        valid_moves.append((x + 1, y))
    if y > 0:  # Can move left
        valid_moves.append((x, y - 1))
    if y < len(grid[0]) - 1:  # Can move right
        valid_moves.append((x, y + 1))
    return valid_moves

# Function to check if the puzzle is completed
def is_puzzle_completed(grid):
    correct_grid = list(range(1, grid_size * grid_size)) + [None]  # The correct order of the grid
    flattened_grid = [item for row in grid for item in row]  # Flatten the grid to compare easily
    return flattened_grid == correct_grid

# Function to initialize a shuffled grid based on selected size
def init_grid(grid_size):
    # Step 1: Generate the solved grid
    grid = generate_solved_grid(grid_size)
    
    # Step 2: Shuffle the grid using valid moves to ensure solvability
    grid = shuffle_grid(grid, moves=100)
    
    return grid

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (102, 102, 153)
LIGHT_PURPLE = (153, 153, 204)

# Set up fonts
title_font = pygame.font.SysFont("Roboto Mono", 50)
button_font = pygame.font.SysFont("Roboto Mono", 35)
timer_font = pygame.font.SysFont("Roboto Mono", 30)

# Set up clock for frame rate
clock = pygame.time.Clock()

# Game states to control screen transitions
MENU = "menu"
GRID_SELECTION = "grid_selection"
GAME = "game"
COMPLETED = "completed"
current_screen = MENU

grid_size = None  # To store the selected grid size
moves = 0  # To track moves
start_time = None  # To track the start time of the game
total_elapsed_time = 0  # To store the total time once the game is completed

# Function to draw the main menu
def draw_main_menu():
    screen.fill(PURPLE)
    
    # Title
    title_text = title_font.render("Slider Puzzle", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Button configurations
    buttons = ["Classic", "Time Attack", "Leaderboard", "Sound", "How to Play"]
    button_rects = []
    button_width = 250
    button_height = 60
    button_y_start = 150
    button_gap = 30

    for i, text in enumerate(buttons):
        btn_text = button_font.render(text, True, WHITE)
        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y_start + i * (button_height + button_gap), button_width, button_height)
        button_rects.append((btn_rect, text))  # Add button rect and its label (to know which was clicked)
        pygame.draw.rect(screen, LIGHT_PURPLE, btn_rect, border_radius=10)
        screen.blit(btn_text, (btn_rect.x + (button_width - btn_text.get_width()) // 2, btn_rect.y + (button_height - btn_text.get_height()) // 2))

    return button_rects

# Function to check for button clicks
def check_button_click(mouse_pos, button_rects):
    for rect, label in button_rects:
        if rect.collidepoint(mouse_pos):
            return label
    return None

# Function to draw the grid size selection screen
def draw_grid_selection():
    screen.fill(PURPLE)

    # Title
    title_text = title_font.render("Classic", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Button configurations
    grid_sizes = ["3x3", "4x4", "5x5", "6x6", "7x7", "8x8"]
    button_rects = []
    button_width = 250
    button_height = 60
    button_y_start = 150
    button_gap = 20

    for i, size in enumerate(grid_sizes):
        btn_text = button_font.render(size, True, WHITE)
        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, button_y_start + i * (button_height + button_gap), button_width, button_height)
        button_rects.append((btn_rect, size))  # Add button rect and its label (to know which was clicked)
        pygame.draw.rect(screen, LIGHT_PURPLE, btn_rect, border_radius=10)
        screen.blit(btn_text, (btn_rect.x + (button_width - btn_text.get_width()) // 2, btn_rect.y + (button_height - btn_text.get_height()) // 2))

    # Back button
    back_text = button_font.render("<", True, WHITE)
    back_rect = pygame.Rect(20, 20, 40, 40)  # Small button in the corner
    button_rects.append((back_rect, "Back"))
    pygame.draw.rect(screen, LIGHT_PURPLE, back_rect, border_radius=10)
    screen.blit(back_text, (back_rect.x + (40 - back_text.get_width()) // 2, back_rect.y + (40 - back_text.get_height()) // 2))

    return button_rects

# Function to draw the game board
def draw_game_board(grid, elapsed_time):
    global moves

    screen.fill(PURPLE)

    # Dynamically adjust tile size and font size based on grid size
    tile_size = SCREEN_WIDTH // grid_size  # Adjust tile size based on the grid size
    font_size = tile_size // 2  # Adjust font size relative to tile size
    tile_font = pygame.font.SysFont("Roboto Mono", font_size)
    margin = 10

    for i in range(len(grid)):
        for j in range(len(grid[i])): 
            tile = grid[i][j]
            if tile:
                pygame.draw.rect(screen, LIGHT_PURPLE, (j * tile_size + margin, i * tile_size + margin + 100, tile_size - margin, tile_size - margin))
                text = tile_font.render(str(tile), True, WHITE)
                screen.blit(text, (j * tile_size + margin + (tile_size - text.get_width()) // 2, i * tile_size + margin + 100 + (tile_size - text.get_height()) // 2))

    # Display move count
    move_text = button_font.render(f"Moves: {moves}", True, WHITE)
    screen.blit(move_text, (20, 20))

    # Display time
    time_text = timer_font.render(f"Time: {elapsed_time // 60:02}:{elapsed_time % 60:02}", True, WHITE)
    screen.blit(time_text, (SCREEN_WIDTH - 160, 20))

    # Back button
    back_text = button_font.render("<", True, WHITE)
    back_rect = pygame.Rect(20, 60, 40, 40)  # Small button in the corner
    pygame.draw.rect(screen, LIGHT_PURPLE, back_rect, border_radius=10)
    screen.blit(back_text, (back_rect.x + (40 - back_text.get_width()) // 2, back_rect.y + (40 - back_text.get_height()) // 2))

    return back_rect

# Function to draw the "Completed" screen
def draw_completion_screen(elapsed_time):
    screen.fill(PURPLE)
    
    # Completion message
    completed_text = title_font.render("Completed!", True, WHITE)
    congrats_text = button_font.render("CONGRATULATIONS <3", True, WHITE)
    screen.blit(completed_text, (SCREEN_WIDTH // 2 - completed_text.get_width() // 2, 150))
    screen.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, 230))
    
    # Display moves
    moves_text = button_font.render(f"Total Moves: {moves}", True, WHITE)
    screen.blit(moves_text, (SCREEN_WIDTH // 2 - moves_text.get_width() // 2, 300))

    # Display time taken
    time_text = timer_font.render(f"Total Time: {elapsed_time // 60:02}:{elapsed_time % 60:02}", True, WHITE)
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 350))

    # Back to Menu button
    back_text = button_font.render("Back to Menu", True, WHITE)
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(screen, LIGHT_PURPLE, back_rect, border_radius=10)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 410))

    # Play Again button
    play_again_text = button_font.render("Play Again", True, WHITE)
    play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 470, 200, 50)
    pygame.draw.rect(screen, LIGHT_PURPLE, play_again_rect, border_radius=10)
    screen.blit(play_again_text, (SCREEN_WIDTH // 2 - play_again_text.get_width() // 2, 480))

    return back_rect, play_again_rect

# Main loop
def main():
    global current_screen, grid_size, moves, start_time, total_elapsed_time
    running = True
    grid = None  # Initialize grid

    while running:
        elapsed_time = 0
        if current_screen == MENU:
            button_rects = draw_main_menu()  # Draw the buttons and retrieve their rects
        elif current_screen == GRID_SELECTION:
            button_rects = draw_grid_selection()  # Draw grid size selection screen
        elif current_screen == GAME:
            elapsed_time = int(time.time() - start_time)  # Calculate elapsed time
            back_rect = draw_game_board(grid, elapsed_time)  # Draw the game board and get back_rect
        
            # Check if the puzzle is completed
            if is_puzzle_completed(grid):
                total_elapsed_time = elapsed_time  # Store the total time once the game is completed
                current_screen = COMPLETED
                play_completion_sound()  # Play completion sound if available

        elif current_screen == COMPLETED:
            back_rect, play_again_rect = draw_completion_screen(total_elapsed_time)  # Show the completion screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check if the mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()  # Get the mouse position

                if current_screen == MENU:
                    clicked_button = check_button_click(mouse_pos, button_rects)  # Check if any button was clicked

                    if clicked_button:
                        if clicked_button == "Classic":
                            current_screen = GRID_SELECTION  # Switch to grid size selection screen
                        elif clicked_button == "Time Attack":
                            print("Time Attack mode selected!")  # Placeholder
                        elif clicked_button == "Leaderboard":
                            print("Leaderboard selected!")  # Placeholder
                        elif clicked_button == "Sound":
                            toggle_sound()
                            print("Toggled sound!")
                        elif clicked_button == "How to Play":
                            print("How to Play selected!")  # Placeholder

                elif current_screen == GRID_SELECTION:
                    clicked_button = check_button_click(mouse_pos, button_rects)

                    if clicked_button == "Back":
                        current_screen = MENU  # Go back to main menu
                    elif clicked_button:
                        # Set grid size and initialize grid
                        grid_size = int(clicked_button[0])
                        grid = init_grid(grid_size)
                        moves = 0
                        start_time = time.time()  # Start the timer
                        current_screen = GAME  # Go to the game proper

                elif current_screen == GAME:
                    if back_rect.collidepoint(mouse_pos):
                        current_screen = GRID_SELECTION  # Go back to grid selection
                    else:
                        # Get tile clicked
                        tile_x = (mouse_pos[1] - 100) // (SCREEN_WIDTH // grid_size)
                        tile_y = mouse_pos[0] // (SCREEN_WIDTH // grid_size)
                        if 0 <= tile_x < grid_size and 0 <= tile_y < grid_size:
                            move_tile(grid, (tile_x, tile_y))  # Play sound when the tile moves

                elif current_screen == COMPLETED:
                    # Handle the back to menu and play again clicks
                    if back_rect.collidepoint(mouse_pos):
                        current_screen = MENU  # Go back to the main menu
                    elif play_again_rect.collidepoint(mouse_pos):
                        # Reset the game and start over
                        grid = init_grid(grid_size)
                        moves = 0
                        start_time = time.time()  # Reset the timer
                        current_screen = GAME

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
