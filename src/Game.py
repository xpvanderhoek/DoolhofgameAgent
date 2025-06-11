import random
import pygame as pg
import time

class Agent:
    def __init__(self, veld, start, doel):
        self.veld = veld
        self.start = start
        self.doel = doel
        self.alle_Qwaardes = {}
        self.learning_rate = 0.9
        self.discount = 0.9
        self.kans_willekeurig = 0.001
        self.max_steps = 3000
        self.reset()

    def reset(self):
        self.x, self.y = self.start
        self.steps = 0
        self.bezochte_staten = set()

    def afstand_tot_doel(self, x, y):
        dx = abs(x - self.doel[0])
        dy = abs(y - self.doel[1])
        return dx + dy

    def get_QWaardes(self, state):
        if state not in self.alle_Qwaardes:
            self.alle_Qwaardes[state] = [0, 0, 0, 0]  # up, down, left, right
        return self.alle_Qwaardes[state]

    def kies_actie(self):
        if random.random() < self.kans_willekeurig:
            return random.choice([0, 1, 2, 3])
        else:
            qs = self.get_QWaardes((self.x, self.y))
            return qs.index(max(qs))

    def doe_actie(self, actie):
        oudeX, oudeY = [(0, -1), (0, 1), (-1, 0), (1, 0)][actie]
        nieuweX, nieuweY = self.x + oudeX, self.y + oudeY

        # Buiten de map? Straf
        if not (0 <= nieuweX < len(self.veld[0]) and 0 <= nieuweY < len(self.veld)):
            return -10, (self.x, self.y), False

        nieuweLocatie = self.veld[nieuweY][nieuweX]
        oude_afstand = self.afstand_tot_doel(self.x, self.y)
        nieuwe_afstand = self.afstand_tot_doel(nieuweX, nieuweY)

        # Bepaal beloning
        if nieuweLocatie == "#":
            reward = -10
        elif nieuweLocatie == "X":
            reward = -20
        elif nieuweLocatie == "G":
            reward = 10000
        else:
            if nieuwe_afstand < oude_afstand:
                reward = 1
            elif nieuwe_afstand == oude_afstand:
                reward = -2  # extra straf voor geen voortgang
            elif oude_afstand < nieuwe_afstand:
                reward = -1
            else:
                reward = -1

        done = nieuweLocatie == "G"

        return reward, (nieuweX, nieuweY), done

    def leer(self, screen=None, delay=0):
        self.reset()
        total_reward = 0
        for _ in range(self.max_steps):
            locatie = (self.x, self.y)
            actie = self.kies_actie()
            reward, new_locatie, done = self.doe_actie(actie)

            if self.veld[new_locatie[1]][new_locatie[0]] == "#":
                new_locatie = (self.x, self.y)

            if new_locatie in self.bezochte_staten:
                reward -= 3
            self.bezochte_staten.add(new_locatie)

            old_q = self.get_QWaardes(locatie)[actie]
            future_q = max(self.get_QWaardes(new_locatie))
            nieuwe_q = (1 - self.learning_rate) * old_q + self.learning_rate * (reward + self.discount * future_q)
            self.alle_Qwaardes[locatie][actie] = nieuwe_q

            self.x, self.y = new_locatie

            if screen:
                tekenVeld()
                teken_q_waardes(agent)
                pg.display.flip()
                rect = pg.Rect(self.x * rij_grootte, self.y * kolom_grootte, rij_grootte, kolom_grootte)
                pg.draw.rect(screen, YELLOW, rect)
                pg.display.flip()
                if delay > 0:
                    time.sleep(delay)

            if done:
                break
            else:
                total_reward += reward
        return total_reward


# =====================================================================================================================
# ======================================== Einde Agent ================================================================
# =====================================================================================================================


def maakVeld(rijen, kolommen):
    global veld
    veld = [["#" for _ in range(kolommen)] for _ in range(rijen)]

    pad = []
    start = (0, 0)
    einde = (kolommen - 1, rijen - 1)
    bezocht = set()


    def dfs(x, y):
        pad.append((x, y))
        if (x, y) == einde:
            return True
        richtingen = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(richtingen)
        for oudeX, oudeY in richtingen:
            nieuweX, nieuweY = x + oudeX, y + oudeY
            if 0 <= nieuweX < kolommen and 0 <= nieuweY < rijen and (nieuweX, nieuweY) not in bezocht:
                bezocht.add((nieuweX, nieuweY))
                if dfs(nieuweX, nieuweY):
                    return True
        pad.pop()
        return False

    bezocht.add(start)
    dfs(*start)

    for (x, y) in pad:
        if (x, y) == start:
            veld[y][x] = "S"
        elif (x, y) == einde:
            veld[y][x] = "G"
        else:
            veld[y][x] = " "


    for y in range(rijen):
        for x in range(kolommen):
            if (x, y) not in pad:
                veld[y][x] = random.choices(["#", "X", " "], weights=[40, 30, 30])[0]


def tekenVeld():
    for y in range(Rijen):
        for x in range(Kolommen):
            waarde = veld[y][x]
            kleur = {
                "S": GRAY,
                " ": GRAY,
                "#": BLACK,
                "X": RED,
                "G": GREEN
            }[waarde]
            rect = pg.Rect(x * rij_grootte, y * kolom_grootte, rij_grootte, kolom_grootte)
            pg.draw.rect(screen, kleur, rect)
            pg.draw.rect(screen, BLACK, rect, 1)

def teken_q_waardes(agent):
    font = pg.font.SysFont("Arial", 12)
    for y in range(Rijen):
        for x in range(Kolommen):
            state = (x, y)
            if state in agent.alle_Qwaardes:
                qs = agent.alle_Qwaardes[state]
                waarde = max(qs)
                tekst = font.render(f"{waarde:.1f}", True, BLUE)
                screen.blit(tekst, (x * rij_grootte + 2, y * kolom_grootte + 2))

def visualiseer_pad(agent, screen, delay=0.1):
    x, y = agent.start
    pad = []
    for _ in range(200):
        pad.append((x, y))
        if (x, y) == agent.doel:
            break
        actie = agent.get_QWaardes((x, y)).index(max(agent.get_QWaardes((x, y))))
        oudeX, oudeY = [(0, -1), (0, 1), (-1, 0), (1, 0)][actie]
        nieuweX, nieuweY = x + oudeX, y + oudeY
        if not (0 <= nieuweX < Kolommen and 0 <= nieuweY < Rijen):
            break
        x, y = nieuweX, nieuweY

    for x, y in pad:
        tekenVeld()
        rect = pg.Rect(x * rij_grootte, y * kolom_grootte, rij_grootte, kolom_grootte)
        pg.draw.rect(screen, LIGHT_BLUE, rect)
        pg.display.flip()
        time.sleep(delay)


# Vraag input
Kolommen = int(input("Hoeveel vakjes wil je de rij hebben (Horizontaal): "))
Rijen = int(input("Hoeveel vakjes wil je de kolom hebben (Verticaal): "))

# Game opzet
pg.init()
WIDTH, HEIGHT = 1200, 800
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Grid van {}x{} vakjes".format(Rijen, Kolommen))
clock = pg.time.Clock()

# Kleuren
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (127, 127, 127)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (0, 0, 127)

rij_grootte = WIDTH // Kolommen
kolom_grootte = HEIGHT // Rijen

veld = []

maakVeld(Rijen, Kolommen)
agent = Agent(veld, (0, 0), (Kolommen - 1, Rijen - 1))

print("Training gestart...")
episodes = 300
for episode in range(episodes):
    score = agent.leer(screen, delay=0.002)
    if (episode + 1) % 10 == 0:
        print(f"Episode {episode+1}/{episodes}, Score: {score}")

print("Training klaar! Visualiseer beste pad...")
i = 0
# Toon beste pad
while i < 10:
    visualiseer_pad(agent, screen)
    i += 1

# Wacht tot venster sluit
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    clock.tick(30)

pg.quit()


