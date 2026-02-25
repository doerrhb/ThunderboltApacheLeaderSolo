import random

# ==========================================================
# UTILITY
# ==========================================================

def roll_d10():
    return random.randint(1, 10)

# ==========================================================
# HEX MAP + RIDGE SYSTEM
# ==========================================================

HEX_CONNECTIONS = {
    1: [2,3,4],
    2: [1,4,5],
    3: [1,4,6],
    4: [1,2,3,5,6,7],
    5: [2,4,7],
    6: [3,4,7],
    7: [4,5,6]
}

RIDGES = {
    frozenset((3,4)),
    frozenset((4,5)),
}

def is_adjacent(h1, h2):
    return h2 in HEX_CONNECTIONS[h1]

def ridge_blocks(h1, h2):
    return frozenset((h1, h2)) in RIDGES

def has_line_of_sight(h1, h2):
    if h1 == h2:
        return True
    if is_adjacent(h1, h2):
        if ridge_blocks(h1, h2):
            return False
        return True
    return False

# ==========================================================
# CLASSES
# ==========================================================

class Pilot:
    def __init__(self, name, strike, cannon, cool):
        self.name = name
        self.strike = strike
        self.cannon = cannon
        self.cool = cool
        self.stress = 0

    def add_stress(self, amount):
        self.stress += amount
        print(f">>> {self.name} gains {amount} STRESS (Total: {self.stress})")


class Aircraft:
    def __init__(self, name, speed, structure_limit):
        self.name = name
        self.speed = speed
        self.structure = 0
        self.structure_limit = structure_limit
        self.altitude = "HIGH"
        self.hex = 4

    def move(self, new_hex):
        if new_hex in HEX_CONNECTIONS[self.hex]:
            self.hex = new_hex
            print(f">>> {self.name} moved to hex {self.hex}")
        else:
            print("Invalid move.")

    def change_altitude(self):
        self.altitude = "LOW" if self.altitude == "HIGH" else "HIGH"
        print(f">>> Altitude now {self.altitude}")

    def take_structure_hit(self):
        self.structure += 1
        print(f">>> {self.name} takes STRUCTURE ({self.structure}/{self.structure_limit})")

    def destroyed(self):
        return self.structure >= self.structure_limit


class EnemyUnit:
    def __init__(self, name, icon, hp, strike_def, cannon_def, attack_value, hex_position):
        self.name = name
        self.icon = icon
        self.hp = hp
        self.strike_def = strike_def
        self.cannon_def = cannon_def
        self.attack_value = attack_value
        self.hex = hex_position
        self.alive = True

    def take_hit(self):
        self.hp -= 1
        print(f">>> {self.name} takes 1 HIT (HP {self.hp})")
        if self.hp <= 0:
            self.alive = False
            print(f">>> {self.name} DESTROYED")

# ==========================================================
# BATTALION
# ==========================================================

class Battalion:
    def __init__(self, units):
        self.units = units

    def alive_units(self):
        return [u for u in self.units if u.alive]

    def total_hp(self):
        return sum(u.hp for u in self.units if u.alive)

    def status(self):
        hp = self.total_hp()
        if hp == 0:
            return "DESTROYED"
        elif hp <= 2:
            return "HALF"
        else:
            return "FULL"

# ==========================================================
# ASCII MAP RENDERER (100% SAFE)
# ==========================================================

def render_map():

    hex_contents = {i: [] for i in range(1,8)}

    for ac in aircraft_list:
        alt = "H" if ac.altitude == "HIGH" else "L"
        hex_contents[ac.hex].append(f"A{alt}")

    for e in enemies:
        if e.alive:
            hex_contents[e.hex].append(e.icon)

    def cell(n):
        content = ",".join(hex_contents[n])
        if not content:
            content = ""
        return f"{n}:{content}".ljust(10)

    print("\n")
    print("                 ________        ________")
    print("                /        \\      /        \\")
    print(f"               / {cell(1)} \\______/ {cell(2)} \\")
    print("               \\________/      \\________/")
    print("          ________        ________        ________")
    print("         /        \\______/        \\______/        \\")
    print(f"        / {cell(3)} \\      / {cell(4)} \\      / {cell(5)} \\")
    print("        \\________/      \\________/      \\________/")
    print("               ________        ________")
    print("              /        \\______/        \\")
    print(f"             / {cell(6)} \\      / {cell(7)} \\")
    print("             \\________/      \\________/")
    print()

    print("Legend:")
    print("AH = Aircraft High")
    print("AL = Aircraft Low")
    print("T  = Tank")
    print("G  = AAA")
    print("Ridges:", [tuple(r) for r in RIDGES])
    print()

# ==========================================================
# SETUP
# ==========================================================

pilot = Pilot("Viper", strike=2, cannon=2, cool=1)

aircraft_list = [
    Aircraft("A-10", "FAST", 4)
]

enemies = [
    EnemyUnit("Tank", "T", 2, 6, 5, 3, 3),
    EnemyUnit("AAA", "G", 2, 7, 6, 4, 5)
]

battalion = Battalion(enemies)
loiter = 6

# ==========================================================
# COMBAT
# ==========================================================

def cover_bonus(target):
    bonus = 0
    for other in enemies:
        if other.alive and other != target:
            if other.hex == target.hex:
                bonus += 1
            elif is_adjacent(other.hex, target.hex):
                bonus += 1
    return bonus


def player_attack(ac, target, attack_type):

    if not has_line_of_sight(ac.hex, target.hex):
        print(">>> Ridge blocks line of sight!")
        return

    if attack_type == "strike":
        base = pilot.strike
        target_number = target.strike_def
    else:
        if ac.altitude != "LOW":
            print(">>> Must be LOW for Cannon.")
            return
        base = pilot.cannon
        target_number = target.cannon_def

    target_number += cover_bonus(target)

    roll = roll_d10()
    total = roll + base

    print(f"Roll {roll} + {base} = {total} (Need {target_number})")

    if total >= target_number:
        target.take_hit()
    else:
        print("Missed.")


def enemy_fire(ac):

    for e in enemies:
        if not e.alive:
            continue

        if not has_line_of_sight(e.hex, ac.hex):
            continue

        if not is_adjacent(e.hex, ac.hex) and e.hex != ac.hex:
            continue

        print(f"{e.name} fires!")

        roll = roll_d10()
        print("Enemy roll:", roll)

        if roll <= e.attack_value:
            ac.take_structure_hit()
        elif roll <= e.attack_value + 2:
            pilot.add_stress(1)
        else:
            print("No effect.")

        if ac.destroyed():
            return

# ==========================================================
# MAIN LOOP
# ==========================================================

print("=== TAL ENGINE V8 ===")

while loiter > 0:

    print("\n====================================")
    print(f"LOITER: {loiter}")
    print("Battalion:", battalion.status())
    render_map()

    if battalion.total_hp() == 0:
        break

    print("--- FAST AIRCRAFT PHASE ---")

    for ac in aircraft_list:

        if ac.speed != "FAST":
            continue

        print(f"{ac.name} at hex {ac.hex} altitude {ac.altitude}")

        action = input("M)ove A)ltitude F)ire 0)Skip > ").upper()

        if action == "M":
            print("Adjacent:", HEX_CONNECTIONS[ac.hex])
            ac.move(int(input("Move to hex: ")))
        elif action == "A":
            ac.change_altitude()
        elif action == "F":
            targets = battalion.alive_units()
            for i,e in enumerate(targets):
                print(f"{i+1}) {e.name} (hex {e.hex})")
            choice = int(input("Target: ")) - 1
            target = targets[choice]
            atk = input("1)Strike 2)Cannon > ")
            player_attack(ac, target, "strike" if atk=="1" else "cannon")

    print("--- ENEMY FIRE ---")

    for ac in aircraft_list:
        enemy_fire(ac)
        if ac.destroyed():
            break

    if any(ac.destroyed() for ac in aircraft_list):
        break

    loiter -= 1

print("\n=== MISSION END ===")
print("Battalion:", battalion.status())
print("Stress:", pilot.stress)
for ac in aircraft_list:
    print(ac.name, "Structure:", ac.structure)