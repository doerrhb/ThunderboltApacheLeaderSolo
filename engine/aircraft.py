import pygame
import os
from engine.config import *

class Aircraft:

    def __init__(self, name, image, hex_index):
        self.name = name
        self.original_image = image
        self.hex_index = hex_index
        self.selected = False
        self.altitude = "L"

        self.image = pygame.transform.smoothscale(
            self.original_image,
            (AIRCRAFT_RENDER_SIZE, AIRCRAFT_RENDER_SIZE)
        )

    def draw(self, screen, hex_positions, stack_index, stack_count):

        hex_x, hex_y = hex_positions[self.hex_index]

        center_x = hex_x + HEX_WIDTH // 2
        center_y = hex_y + HEX_HEIGHT // 2 - 6

        offset_spacing = 18
        total_width = (stack_count - 1) * offset_spacing
        offset_x = (stack_index * offset_spacing) - (total_width // 2)

        x = center_x - AIRCRAFT_RENDER_SIZE // 2 + offset_x
        y = center_y - AIRCRAFT_RENDER_SIZE // 2

        screen.blit(self.image, (x, y))

        # Thin white selection outline
        if self.selected:
            rect = pygame.Rect(x, y, AIRCRAFT_RENDER_SIZE, AIRCRAFT_RENDER_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    def contains_point(self, pos, hex_positions, stack_index, stack_count):

        hex_x, hex_y = hex_positions[self.hex_index]

        center_x = hex_x + HEX_WIDTH // 2
        center_y = hex_y + HEX_HEIGHT // 2 - 6

        offset_spacing = 18
        total_width = (stack_count - 1) * offset_spacing
        offset_x = (stack_index * offset_spacing) - (total_width // 2)

        x = center_x - AIRCRAFT_RENDER_SIZE // 2 + offset_x
        y = center_y - AIRCRAFT_RENDER_SIZE // 2

        rect = pygame.Rect(x, y, AIRCRAFT_RENDER_SIZE, AIRCRAFT_RENDER_SIZE)
        return rect.collidepoint(pos)


def load_aircraft_images():
    aircraft_path = os.path.join(ASSET_PATH, "aircraft")
    aircraft_images = {}

    for file in sorted(os.listdir(aircraft_path)):
        if file.endswith(".png"):
            name = file.replace(".png", "").upper()
            img = pygame.image.load(
                os.path.join(aircraft_path, file)
            ).convert_alpha()
            aircraft_images[name] = img

    return aircraft_images