# main.py

import pygame
import time
from src.modes.classic import init_classic_mode, handle_classic_game
from src.modes.time_attack import init_time_attack_mode, handle_time_attack_game
from src.modes.htp import draw_htp_screen
from utils.sound import toggle_sound
from src.modes.gameboard import draw_game_board

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up display
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slider Puzzle")

# Define Colors
WHITE = (255, 255, 255)
LIGHT_PURPLE = (153, 153, 204)
PURPLE = (102, 102, 153)

# Set up fonts
title_font = pygame.font.SysFont("Roboto Mono", 50)
button_font = pygame.font.SysFont("Roboto Mono", 35)
timer_font = pygame.font.SysFont("Roboto Mono", 30)

# Game states
MENU = "menu"
CLASSIC = "classic"
TIME_ATTACK = "time_attack"
HOW_TO_PLAY = "htp"
current_screen = MENU

grid_size = None
grid = None
moves = 0
start_time = None

# Function to draw the main menu
def draw_main_menu():
    screen.fill(PURPLE)
    title_text = title_font.render("Slider Puzzle", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    buttons = ["Classic", "Time Attack", "Leaderboard", "Sound", "How to Play"]
    button_rects = []
    for i, text in enumerate(buttons):
        btn_text = button_font.render(text, True, WHITE)
        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, 150 + i * 80, 250, 60)
        button_rects.append((btn_rect, text))
        pygame.draw.rect(screen, LIGHT_PURPLE, btn_rect, border_radius=10)
        screen.blit(btn_text, (btn_rect.x + (250 - btn_text.get_width()) // 2, btn_rect.y + 15))

    return button_rects

# Main loop
def main():
    global current_screen, grid_size, moves, start_time, grid
    running = True

    while running:
        screen.fill(PURPLE)

        if current_screen == MENU:
            button_rects = draw_main_menu()
        elif current_screen == CLASSIC:
            elapsed_time = int(time.time() - start_time)
            game_completed, moves, _ = handle_classic_game(grid, screen, grid_size, elapsed_time, button_font, timer_font, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, LIGHT_PURPLE)
            if game_completed:
                current_screen = MENU
        elif current_screen == TIME_ATTACK:
            elapsed_time = int(time.time() - start_time)
            game_completed, moves, _ = handle_time_attack_game(grid, screen, grid_size, elapsed_time, button_font, timer_font, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, LIGHT_PURPLE)
            if game_completed:
                current_screen = MENU
        elif current_screen == HOW_TO_PLAY:
            back_rect = draw_htp_screen(screen, title_font, button_font, SCREEN_WIDTH, SCREEN_HEIGHT, PURPLE, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if current_screen == MENU:
                    clicked_button = next((label for rect, label in button_rects if rect.collidepoint(mouse_pos)), None)
                    if clicked_button == "Classic":
                        current_screen = CLASSIC
                        grid_size = 3
                        grid = init_classic_mode(grid_size)
                        start_time = time.time()
                    elif clicked_button == "Time Attack":
                        current_screen = TIME_ATTACK
                        grid_size = 3
                        grid = init_time_attack_mode(grid_size)
                        start_time = time.time()
                    elif clicked_button == "How to Play":
                        current_screen = HOW_TO_PLAY
                    elif clicked_button == "Sound":
                        toggle_sound()

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
