import random

# =========================
# Utility
# =========================

def roll_d10():
    return random.randint(1, 10)


# =========================
# Battlefield
# =========================

HEX_CONNECTIONS = {
    1: [2,3,4],
    2: [1,4,5],
    3: [1,4,6],
    4: [1,2,3,5,6,7],
    5: [2,4,7],
    6: [3,4,7],
    7: [4,5,6]
}

def is_adjacent(h1, h2):
    return h2 in HEX_CONNECTIONS[h1]


# =========================
# Classes
# =========================

class Pilot:
    def __init__(self, name, strike, cannon, cool):
        self.name = name
        self.strike = strike
        self.cannon = cannon
        self.cool = cool
        self.stress = 0

    def add_stress(self, amount):
        self.stress += amount
        print(f"{self.name} gains {amount} stress (Total: {self.stress})")


class Aircraft:
    def __init__(self, name, structure_limit):
        self.name = name
        self.structure = 0
        self.structure_limit = structure_limit
        self.altitude = "HIGH"
        self.hex = 4  # start center

    def change_altitude(self):
        self.altitude = "LOW" if self.altitude == "HIGH" else "HIGH"
        print(f"Altitude changed to {self.altitude}")

    def move(self, new_hex):
        if new_hex in HEX_CONNECTIONS[self.hex]:
            self.hex = new_hex
            print(f"Moved to hex {self.hex}")
        else:
            print("Invalid move.")

    def take_structure_hit(self):
        self.structure += 1
        print(f"{self.name} takes 1 STRUCTURE hit! ({self.structure}/{self.structure_limit})")

    def is_crashed(self):
        return self.structure >= self.structure_limit


class EnemyUnit:
    def __init__(self, name, attack_hits, attack_type, attack_number, value, range_max, hex_position):
        self.name = name
        self.attack_hits = attack_hits
        self.attack_type = attack_type
        self.attack_number = attack_number
        self.value = value
        self.range_max = range_max
        self.hex = hex_position
        self.alive = True

    def destroy(self):
        self.alive = False
        print(f"{self.name} DESTROYED!")

    def in_range(self, aircraft_hex):
        if aircraft_hex == self.hex:
            return True
        if self.range_max == 1 and is_adjacent(self.hex, aircraft_hex):
            return True
        return False


# =========================
# Setup
# =========================

pilot = Pilot("Viper", strike=2, cannon=2, cool=1)
aircraft = Aircraft("A-10", structure_limit=4)

enemies = [
    EnemyUnit("Tank", 1, "light", 6, 2, range_max=0, hex_position=3),
    EnemyUnit("AAA", 2, "heavy", 7, 2, range_max=1, hex_position=5)
]

loiter = 6

print("=== TUTORIAL MISSION V3 ===")


# =========================
# Mission Loop
# =========================

while loiter > 0:

    print("\n===================================")
    print(f"LOITER: {loiter}")
    print(f"Aircraft Hex: {aircraft.hex}")
    print(f"Altitude: {aircraft.altitude}")
    print()

    alive = [e for e in enemies if e.alive]

    if not alive:
        print("All enemies destroyed!")
        break

    print("Enemies:")
    for i, e in enumerate(alive):
        print(f"{i+1}) {e.name} (Hex {e.hex})")

    print("\nActions:")
    print("M) Move")
    print("A) Change Altitude")
    print("0) End Turn")
    print("Or select enemy number to attack")

    choice = input("> ").strip().upper()

    # MOVE
    if choice == "M":
        print(f"Adjacent hexes: {HEX_CONNECTIONS[aircraft.hex]}")
        try:
            new_hex = int(input("Move to hex: "))
            aircraft.move(new_hex)
        except:
            print("Invalid input.")
        continue

    # ALTITUDE
    if choice == "A":
        aircraft.change_altitude()
        continue

    # END TURN
    if choice == "0":
        pass

    # ATTACK
    else:
        try:
            target = alive[int(choice)-1]
        except:
            print("Invalid selection.")
            continue

        # Range check
        in_same_hex = aircraft.hex == target.hex
        adjacent = is_adjacent(aircraft.hex, target.hex)

        print("\nAttack Type:")
        print("1) Strike (range 0-1)")
        print("2) Cannon (range 0 only, LOW altitude required)")
        atk_choice = input("> ")

        if atk_choice == "1":
            if not (in_same_hex or adjacent):
                print("Out of range for Strike.")
                continue
            skill = pilot.strike

        elif atk_choice == "2":
            if aircraft.altitude != "LOW":
                print("Must be LOW altitude for Cannon.")
                continue
            if not in_same_hex:
                print("Cannon requires same hex.")
                continue
            skill = pilot.cannon

        else:
            print("Invalid attack type.")
            continue

        roll = roll_d10()
        total = roll + skill

        print(f"Roll {roll} + Skill {skill} = {total}")

        if total >= target.attack_number:
            target.destroy()
        else:
            print("Missed!")

    # =========================
    # Enemy Phase
    # =========================

    print("\n--- Enemy Attacks ---")

    for enemy in enemies:
        if enemy.alive and enemy.in_range(aircraft.hex):

            print(f"{enemy.name} fires!")

            for _ in range(enemy.attack_hits):

                if enemy.attack_type == "light":
                    result = random.choice(["stress", "structure", "none"])
                else:
                    result = random.choice(["structure", "structure", "stress"])

                if result == "stress":
                    pilot.add_stress(1)
                elif result == "structure":
                    aircraft.take_structure_hit()
                else:
                    print("No effect.")

                if aircraft.is_crashed():
                    print("AIRCRAFT CRASHED!")
                    break

        if aircraft.is_crashed():
            break

    if aircraft.is_crashed():
        break

    loiter -= 1


# =========================
# Mission Result
# =========================

print("\n=== MISSION COMPLETE ===")

if aircraft.is_crashed():
    print("Mission Failed.")
else:
    remaining = sum(e.value for e in enemies if e.alive)

    if remaining == 0:
        print("Battalion Destroyed!")
    elif remaining <= 2:
        print("Battalion Reduced!")
    else:
        print("Battalion Survived.")

print(f"Stress: {pilot.stress}")
print(f"Structure: {aircraft.structure}")