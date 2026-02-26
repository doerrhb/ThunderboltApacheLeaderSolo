import random
from engine.aircraft import Aircraft

ADJACENCY = {
    0: [1, 3],
    1: [0, 2, 3, 4],
    2: [1, 4],
    3: [0, 1, 4, 6],
    4: [1, 2, 3, 5, 6, 7],
    5: [2, 4, 7],
    6: [3, 4, 8],
    7: [4, 5, 8],
    8: [6, 7],
}

class GroundUnit:
    def __init__(self, hex_index):
        self.hex_index = hex_index
        self.hp = 2

class GameState:

    def __init__(self, aircraft_images):

        self.aircraft = []
        self.selected_aircraft = None
        self.enemy = GroundUnit(4)
        self.turn = "PLAYER"

        keys = list(aircraft_images.keys())
        if len(keys) >= 1:
            self.aircraft.append(Aircraft(keys[0], aircraft_images[keys[0]], 0))

    # ---------------------------------

    def handle_click(self, pos, hex_positions, log):

        if self.turn != "PLAYER":
            return

        # Aircraft selection
        for hex_index in range(len(hex_positions)):
            stack = [a for a in self.aircraft if a.hex_index == hex_index]

            for i, aircraft in enumerate(stack):
                if aircraft.contains_point(pos, hex_positions, i, len(stack)):
                    self.selected_aircraft = aircraft
                    aircraft.selected = True
                    log(f"{aircraft.name} selected at HEX {hex_index}")
                    return

        # Movement attempt
        if self.selected_aircraft:
            clicked_hex = self.get_clicked_hex(pos, hex_positions)

            if clicked_hex is not None:
                current_hex = self.selected_aircraft.hex_index

                if clicked_hex in ADJACENCY[current_hex]:
                    self.selected_aircraft.hex_index = clicked_hex
                    log(f"{self.selected_aircraft.name} MOVES: HEX {current_hex} -> HEX {clicked_hex}")
                else:
                    log("Invalid move: not adjacent")

    # ---------------------------------

    def get_clicked_hex(self, pos, hex_positions):

        for index, (x, y) in enumerate(hex_positions):
            if x <= pos[0] <= x + 244 and y <= pos[1] <= y + 282:
                return index

        return None

    # ---------------------------------

    def attack(self, log):

        if self.turn != "PLAYER":
            return

        if not self.selected_aircraft:
            log("Attack aborted: no aircraft selected")
            return

        if self.selected_aircraft.hex_index != self.enemy.hex_index:
            log("Attack aborted: no enemy in hex")
            return

        roll = random.randint(1, 6)
        log(f"{self.selected_aircraft.name} ATTACKS (d6 roll = {roll})")

        if roll >= 4:
            self.enemy.hp -= 1
            log("HIT CONFIRMED")
        else:
            log("MISS")

        if self.enemy.hp <= 0:
            log("TARGET DESTROYED")

    # ---------------------------------

    def end_turn(self, log):

        if self.turn == "PLAYER":
            self.turn = "ENEMY"
            log("---- ENEMY TURN ----")
        else:
            self.turn = "PLAYER"
            log("---- PLAYER TURN ----")

    # ---------------------------------

    def draw_aircraft(self, screen, hex_positions):

        for hex_index in range(len(hex_positions)):
            stack = [a for a in self.aircraft if a.hex_index == hex_index]

            for i, aircraft in enumerate(stack):
                aircraft.draw(screen, hex_positions, i, len(stack))

    # ---------------------------------

    def draw_enemy(self, screen, hex_positions, font):

        if self.enemy.hp <= 0:
            return

        x, y = hex_positions[self.enemy.hex_index]
        center_x = x + 122
        center_y = y + 120

        pygame = __import__("pygame")
        pygame.draw.circle(screen, (200, 0, 0), (center_x, center_y), 25)

        hp_text = font.render(str(self.enemy.hp), True, (255, 255, 255))
        screen.blit(hp_text, (center_x - 8, center_y - 10))