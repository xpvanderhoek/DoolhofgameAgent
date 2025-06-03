import random

import pygame as pg

# Vraag het aantal rijen en kolommen
try:
    Rijen = int(input("Hoeveel vakjes wil je de rij hebben (Horizontaal): "))
    Kolommen = int(input("Hoeveel vakjes wil je de kolom hebben (Verticaal): "))
except:
    print("Onjuiste invoer")
    exit()


# Game opzet
pg.init()
WIDTH, HEIGHT = 1200, 800
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Grid van {}x{} vakjes".format(Rijen, Kolommen))
clock = pg.time.Clock()

# Kleuren (vakjes)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (127, 127, 127)

# Veld maken
def maakVeld(rijen, kolommen):
    rij_grootte = WIDTH // kolommen
    kolom_grootte = HEIGHT // rijen

    for x in range(kolommen):
        for y in range(rijen):
            if x == 0 and y == 0:
                kleur = GRAY  # Startpositie
            elif x == kolommen - 1 and y == rijen - 1:
                kleur = GREEN  # Doelpositie
            else:
                kleur = random.choices([GRAY, BLACK, RED], weights=[70, 15, 15], k=1)[0]

            rect = pg.Rect(x * rij_grootte, y * kolom_grootte, rij_grootte, kolom_grootte)
            pg.draw.rect(screen, kleur, rect)
            pg.draw.rect(screen, BLACK, rect, 1)


running = True
screen.fill(GRAY)
maakVeld(Rijen, Kolommen)
while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    pg.display.flip()
    clock.tick(30)