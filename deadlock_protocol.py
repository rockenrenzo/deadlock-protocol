
import random
import time
import sys

class DeadlockProtocol:
    def __init__(self):
        self.width = 15
        self.height = 9
        self.turns_left = 60
        self.has_keycard = False
        self.vault_unlocked = False
        self.laser_active = True
        self.status_msg = "Infiltrate the vault [V], bypass the lock, and reach Extract [E}."


        self.player = [1, 1]
        self.terminal = (13, 1)
        self.vault = (13, 7)
        self.extract = (1, 7) 

        self.walls = {
            (4,0), (4,1), (4,2), (4,4), (4,5),
            (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), 
            (6,7), (7,7), (8,7)
        }

        self.lasers = {(4,3), (9,1), (9,2)}


        self.guards = [
            (6, 1, 0, 1),
            (11, 6, 0, -1),
            (3, 8, 1, 0)
        ]

    def slow_print(self, text, delay=0.015):
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def move_guards(self):
        updated_guards = []
        for gx, gy, dx, dy in self.guards:
            nx = gx + dx
            ny = gy + dy 
            if (
                nx < 0 or nx >= self.width or
                ny < 0 or ny >= self.height or 
                (nx,ny) in self.walls or 
                (nx, ny) in self.lasers
            ): 
                dx = -dx
                dy = -dy
                nx = gx + dx
                ny = gy + dy
            updated_guards.append((nx, ny, dx, dy))
        self.guards = updated_guards

    def is_spotted(self):
        px, py = self.player
        for gx, gy, dx, dy in self.guards:
            if (px, py) == (gx, gy) or (px, py) == (gx + dx, gy + dy):
                return True 
        return False

    def run_hack_minigame(self):
        print("\n" + "=" * 50)
        print(" [SECURITY TERMINAL // OVEERRIDE SEQUENCE]")
        print(" Match the 4-bit logic parity to disable vault lock.")
        print("=" * 50)
        target = [random.randint(0, 1) for _ in range (4)]
        attempts = 3

        while attempts > 0:
            guess_raw = input(f" Enter 4 bits e.g., 1010) [{attempts} tries left]: ").strip()
            if len(guess_raw) != 4 or any(c not in "01" for c in guess_raw): 
                print(" [!] Invalid input. Enter exactly four 0s or 1s.")
                continue

            guess = [int(c) for c in guess_raw]
            if guess == target:
                print(" [ACCESS GRANTED] Vault magnetic seal disengaged!")
                time.sleep(0.8)
                return True

            exact = sum(1 for a, b in zip(guess, target) if a ==b)
            print(f" [!] Mismatch: {exact}/4 bits aligned in correct position.")
            attempts -= 1

        print(" [ALRAM] Hack failed! Security surge cost you 5 turns.")
        attempts -= 1
        time.sleep(0.8)
        return False

    def render(self):
        print("\n" + "=" * 52)
        print(f" DEADLOCK PROTOCOL | LOCKDOWN IN: {self.turns_left:02d} TURNS")
        print("=" * 52)

        guard_positions = {(gx,gy) for gx, gy, dx, dy in self.guards}
        vision_tiles = {(gx + dx, gy + dy) for gx, gy, dx, dy in self.guards}

        for y in range(self.height):
            row_chars = []
            for x in range(self.width):
                pos = (x, y)
                if pos == self.player:
                    row_chars.append("@")
                elif pos in guard_positions:
                    row_chars.append("G")
                elif pos in self.walls:
                    row_chars.append("#")
                elif pos in self.lasers:
                    row_chars.append("|" if self.laser_active else ".")
                elif pos == self.terminal:
                    row_chars.append("T")
                elif pos == self.vault:
                    row_chars.append("V")
                elif pos == self.extract:
                    row_chars.append("E")
                elif pos in vision_tiles:
                    row_chars.append("!")
                else:
                    row_chars.append(".")
            print("  " +  " ".join(row_chars)) 

        print("_" * 52)
        print(" LEGEND: @-You G_Guard  !=Sightline  |=Laser T=Terminal  V=Vault E=Exit")
        print(f" STATUS: {self.status_msg}")
        print(" MOVE  : [W/A/S/D] Move  |  [X] Wait 1 turn  |  [Q] Quit")
        print("_" * 52)

    def play(self):
        print("\n" + "*" * 52)
        print("             DEADLOCK PROTOCOL  v1.0")
        print("         Tactical Stealth & Vault Extraction")
        print("*" * 52)
        self.slow_print("1. Reach Terminal [T] to hack the vault keycard.")
        self.slow_print("2. Breach Vault [V] to grab the PHANTOM drive.")
        self.slow_print("3. Escape through Extract [E] before lockdown.\n")
        time.sleep(0.6)

        while self.turns_left > 0:
            self.laser_active = (self.turns_left % 4) in (1,2)
            self.render()

            cmd = input("ACTION > ").strip().upper()
            if cmd == "Q":
                print(" Mission aborted.")
                return

            moves = {"W": (0, -1), "S": (0, 1), "A": (-1, 0), "D": (1,0), "X": (0, 0)}
            if cmd not in moves: 
                self.status_msg = "Invalid key! Use W, A, S, D to move or X to wait."
                continue

            dx, dy = moves[cmd]
            px, py = self.player
            nx = px + dx
            ny = py + dy

            if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height or (nx,ny) in self.walls:
                self.status_msg = "Blocked! by Reinforced walls."
                continue

            self.player = (nx, ny) 
            self.turns_left -= 1

            if self.laser_active and (nx,ny) in self.lasers:
                print("\n [ZAP!] You stepped into an active laser grid! Mission failed.")
                return

            self.move_guards()
            if self.is_spotted():
                self.render()
                print("\n [BUSTED!] Spotted by a security guard! Lockdown triggered.")
                return

            pos = (nx,ny)
            if pos == self.terminal and not self.has_keycard:
                if self.run_hack_minigame():
                    self.has_keycard = True
                    self.status_msg = "Keycard downloaded! Head South to Vault [V]."
                else:
                    self.status_msg = "Terminal lockout reset. Step off and back on to retry."
            elif pos == self.vault:
                if self.has_keycard and not self.vault_unlocked:
                    self.vault_unlocked = True
                    self.status_msg = "PHANTOM Drive secured! Race back to EXTRACT [E] !"
                elif not self.has_keycard:
                    self.status_msg = "Vault locked! Hack Terminal [T] in the northeast first."
                elif pos == self.extract:
                    if self.vault_unlocked:
                        self.render()
                        print("\n" + "=" * 52)
                        print(" EXTRACTION SUCCESSFUL! You escaped with the drive.")
                        print(f" FINAL SCORE: {self.turns_left * 100} PTS ({ self.turns_left} turns remaining)")
                        print("=" * 52)
                        return

                    else: 
                        self.status_msg = "Cannot extract empty-handed! Break Vault [V] first."
                else:
                    self.status_msg = "Lasers cycle every 2 turns. Watch guard sightlines [!]."

            print("\n [TIME EXPIRED!] Blast doors sealed. You are trapped inside.")

if __name__ == "__main__":
    game = DeadlockProtocol()
    game.play()
