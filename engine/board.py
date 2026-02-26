import pygame
import os
from engine.config import *

class Board:

    def __init__(self):
        self.board_img = pygame.image.load(
            os.path.join(ASSET_PATH, "board.png")
        ).convert()

        self.base_img = pygame.image.load(
            os.path.join(ASSET_PATH, "base.png")
        ).convert()

        self.layout = [3, 4, 3]
        self.tiles = self.load_tiles()
        self.map_tiles = self.generate_random_map()

    def load_tiles(self):
        tile_path = os.path.join(ASSET_PATH, "tiles")
        tiles = []

        for file in sorted(os.listdir(tile_path)):
            if file.endswith(".png"):
                tile = pygame.image.load(
                    os.path.join(tile_path, file)
                ).convert_alpha()
                tiles.append(tile)

        return tiles

    def generate_random_map(self):
        import random
        return [[random.choice(self.tiles) for _ in range(count)]
                for count in self.layout]

    def draw(self, screen):

        board_x = (WINDOW_WIDTH - self.board_img.get_width()) // 2
        board_y = (WINDOW_HEIGHT - self.board_img.get_height()) // 2

        screen.blit(self.board_img, (board_x, board_y))

        return board_x, board_y

    def draw_base(self, screen):

        base_x = (WINDOW_WIDTH - self.base_img.get_width()) // 2
        base_y = (WINDOW_HEIGHT - self.base_img.get_height()) // 2

        screen.blit(self.base_img, (base_x, base_y))