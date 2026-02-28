import pygame
import sys

from engine.config import *
from engine.board import Board
from engine.hexgrid import get_hex_positions
from engine.aircraft import load_aircraft_images
from engine.game_state import GameState

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("TAL Engine - Tactical Terminal")

clock = pygame.time.Clock()
terminal_font = pygame.font.SysFont("consolas", 14)

board = Board()
aircraft_images = load_aircraft_images()
game_state = GameState(aircraft_images)

show_base_screen = False
quit_button_rect = pygame.Rect(WINDOW_WIDTH - 160, 20, 140, 50)

log_lines = []

def add_log(text):
    log_lines.append(text)
    if len(log_lines) > 14:
        log_lines.pop(0)

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_TAB:
                show_base_screen = not show_base_screen

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_a:
                game_state.attack(add_log)

            if event.key == pygame.K_e:
                game_state.end_turn(add_log)

        if event.type == pygame.MOUSEBUTTONDOWN:

            if quit_button_rect.collidepoint(event.pos):
                running = False

            if not show_base_screen:
                board_x = (WINDOW_WIDTH - board.board_img.get_width()) // 2
                board_y = (WINDOW_HEIGHT - board.board_img.get_height()) // 2
                hex_positions = get_hex_positions(board_x, board_y, board.layout)
                game_state.handle_click(event.pos, hex_positions, add_log)

    screen.fill((15, 15, 15))

    if show_base_screen:
        board.draw_base(screen)
    else:
        board_x, board_y = board.draw(screen)
        hex_positions = get_hex_positions(board_x, board_y, board.layout)

        # Draw tiles
        index = 0
        for row in board.map_tiles:
            for tile in row:
                x, y = hex_positions[index]
                screen.blit(tile, (x, y))
                index += 1

        game_state.draw_enemy(screen, hex_positions, terminal_font)
        game_state.draw_aircraft(screen, hex_positions)

        # ----- TERMINAL PANEL (BOARD RELATIVE) -----
        log_rect = pygame.Rect(
            board_x + 1300,
            board_y + 5,
            350,
            240
        )

        pygame.draw.rect(screen, (0, 0, 0), log_rect)

        y_offset = log_rect.top + 5
        for line in log_lines:
            text_surface = terminal_font.render("> " + line, True, (0, 255, 0))
            screen.blit(text_surface, (log_rect.left + 8, y_offset))
            y_offset += 16

    pygame.draw.rect(screen, (180, 40, 40), quit_button_rect)
    quit_font = pygame.font.SysFont("arial", 18)
    text = quit_font.render("QUIT", True, (255, 255, 255))
    text_rect = text.get_rect(center=quit_button_rect.center)
    screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()