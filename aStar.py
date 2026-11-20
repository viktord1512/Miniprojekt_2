import heapq
from typing import Final
import random
import pygame
from perlin_noise import PerlinNoise

# ------------------------
# Laver klasser for terræn
# ------------------------
class Terræn:
    def __init__(self, navn, bevægelsesomkostning):
        self.navn = navn
        self.bevægelsesomkostning = bevægelsesomkostning

class Græs:
    def __init__(self):
        super.__init__(self, "græs", 1)

class Vand:
     def __init__(self):
        super.__init__(self, "vand", 2)

class Bjerg:
    def __init__(self):
        super.__init__(self, "bjerg", 3)

class Lava:
    def __init__(self):
        super.__init__(self, "Lava", None)

# -------------------------
# Konstanterne for terrænet
# -------------------------
GRÆS: Final = Græs()       # Konstanten GRÆS defineres ved at fastlåse dens værdi til klassen Græs
VAND: Final = Vand()       # Konstanten VAND defineres ved at fastlåse dens værdi til klassen Vand
BJERG: Final = Bjerg()     # Konstanten BJERG defineres ved at fastlåse dens værdi til klassen Bjerg
LAVA: Final = Lava()       # Konstanten LAVA defineres ved at fastlåse dens værdi til klassen Lava

# --------------------
# Størelsen for pygame
# --------------------
width, height = 50, 25    # Width og height har nu værdierne 50 og 25

# -------------------
# Bestemmelse af seed
# -------------------
seed = random(range(1, 100000))    # Seed bliver valgt imellem 1 og 100000
print("Seed: ", seed)              # Den anvendte seed printes

# ---------------------------
# Bestemmelse af perlin noise
# ---------------------------
perlin_noise = PerlinNoise(octaves=2, seed=seed)           # Her bestemmes oktaven og seed i klassen PerlinNoise
raw = []                                                   # Her laves listen for raw som kommer til at indeholde alle rækkerne
for y in range(height):                                    # Der køres en løkke fra 0 til 25 for hver række i højden
    række = []                                             # Her laves listen for række som kommmer til at indeholde værdierne for hver kolonne i rækken
    for x in range(width):                                 # Der kæres en løkke fra 0 til 50 for hver kolonne i bredden
        række.append(perlin_noise([x/width, y/height]))    # Igennem løkken gentages denne kode der beregner perlin noise for hver x og y
    raw.append(række)                                      # Efter hver række tilføjes rækken til raw-listen

# ------------------------------------------------------------------
# Koden som bestemmer hvordan mappet ser ud ved brug af perlin noise
# ------------------------------------------------------------------
def terræn(value):
    if value < 0.35:    # Hvis 0,35 er større end value bruges den næste linje kode
        return Græs     # Koden retunerer klassen Græs, koden bruger denne information senere
    
    if value < 0.50:    # Hvis 0,5 er større end value bruges den næste linje kode
        return Vand     # Koden retunerer klassen Vand, koden bruger denne information senere
    
    if value < 0.75:    # Hvis 0,75 er større end value bruges den næste linje kode
        return Bjerg    # Koden retunerer klassen Bjerg, koden bruger denne information senere
    else:
        return Lava     # Hvis ingen af de ovenstående stykker kode blev anvendt, retuneres klassen Lava

# ------------------------------------------
# Mappet laves ud fra perlin noise værdierne
# ------------------------------------------
grid = []                                               # Her laves en liste der indeholder alle rækkerne af terrænklasser
for række in raw:                                       # Koden går igennem hver række i raw-listen
    terræn_række = [terræn(value) for value in række]   # Hver værdi i rækken konverteres til en terrænklasse
    grid.append(terræn_række)                           # Terrænrækken tilføjes til grid-listen

# ---------------------------------------------
# Definer start- og slutpunkt for a* algoritmen
# ---------------------------------------------
start = (0, 0)
slut = (width-1, height-1)

# --------------------------------------
# Heurustik funktionen til a* algoritmen
# --------------------------------------
def heurustik(a, b):                            # Her laves heurustik funktionen hvor a og b er koordinaterne for to punkter på mappet
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Her beregnes den manhattanske afstand mellem punkterne a og b

# ------------------------------
# Graf klassen for a* algoritmen
# ------------------------------
class Graf:
    def __init__(self, gitter):                                         #
        self.gitter = gitter                                            #

    def inden_for_rammen(self, position):                               #
        x, y = position                                                 #
        return 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid)   #

    def passable(self, position):                                       #
        x, y = position                                                 #
        return self.grid[y][x].bevægelsesomkostning > 0                 #