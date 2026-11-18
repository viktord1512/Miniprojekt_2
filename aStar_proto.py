import heapq
from typing import Final
import random
import pygame
from perlin_noise import PerlinNoise

# -----------------------
# Lave Terræn med klasser
# -----------------------
class Terræn:
    def __init__(self, navn, bevægelsesomkostning):
        self.navn = navn
        self.bevægelsesomkostning = bevægelsesomkostning

class Græs(Terræn):
    def __init__(self):
        Terræn.__init__(self, "grass", 1)

class Vand(Terræn):
    def __init__(self):
        Terræn.__init__(self, "water", 2)

class Bjerg(Terræn):
    def __init__(self):
        Terræn.__init__(self, "mountain", 3)

class Lava(Terræn):
    def __init__(self):
        Terræn.__init__(self, "lava", None)

# ------------------------------
# Definere konstanter for terræn
# ------------------------------
GRÆS: Final[Græs] = Græs()
VAND: Final[Vand] = Vand()
BJERG: Final[Bjerg] = Bjerg()
LAVA: Final[Lava] = Lava()

# -------------------------------
# Definere størrelsen på terrænet
# -------------------------------
width, height = 50, 25

# ---------------------------
# Generer Perlin noise terræn
# ---------------------------
seed = random.randint(0, 100000) # Genererer en tilfældig seed til Perlin noise generatoren.
print("Seed:", seed)
noise = PerlinNoise(octaves=6, seed=seed) # Initialiserer Perlin noise generatoren med 6 oktaver og den tilfældige seed. Okataver er antallet af lag af støj, der kombineres for at skabe mere kompleks og detaljeret terræn.
raw = [[noise([x/width, y/height]) for x in range(width)] 
       for y in range(height)] # Genererer rå Perlin noise værdier for hver celle i terrænet.



# -------------------------------
# Normaliser Perlin noise værdier
# -------------------------------
low = min(map(min, raw))  # Finder den laveste Perlin noise værdi i terrænet.
high = max(map(max, raw)) # Finder den højeste Perlin noise værdi i terrænet.
raw = [[(v - low) / (high - low) for v in row] for row in raw] # Normaliserer værdierne til intervallet [0, 1]


# -------------------------------------------------------------
# Funktion til at bestemme terræn baseret på Perlin noise værdi
# -------------------------------------------------------------
def terrain(value):
    if value < 0.35: # Hvis værdien er mindre end 0.35, er det vand.
        return VAND
    elif value < 0.65: # Hvis værdien er mellem 0.35 og 0.65, er det græs.
        return GRÆS
    elif value < 0.85: # Hvis værdien er mellem 0.65 og 0.85, er det bjerg.
        return BJERG
    else: # Hvis værdien er større end 0.85, er det lava.
        return LAVA

# ------------------------------------
# Generer grid baseret på Perlin noise
# ------------------------------------
grid = [[terrain(value) for value in row] for row in raw] # Genererer grid baseret på Perlin noise værdierne.


# ---------------------------------------
# Definere start og mål for A* algoritmen
# ---------------------------------------
start = (0, 0) # Startpositionen for A* algoritmen er øverste venstre hjørne af gridet.
goal = (width-1, height-1) # Målpositionen for A* algoritmen er nederste højre hjørne af gridet.
# Jeg minusser 1 fra width og height for at få den sidste celle som mål.
# Jeg gør det da jeg gerne vil have at målet er den celle i nederste højre hjørne af gridet.

# ------------------------------------
# Heuristik funktion til A* algoritmen
# ------------------------------------
def heuristic(a,b): # Heuristik funktionen beregner den estimerede afstand mellem to noder (Manhattan afstand).
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) # Manhattan afstand mellem noderne.

# -------------------------------
# Graph klassen til A* algoritmen
# -------------------------------
class Graph:
    def __init__(self, grid):
        self.grid = grid # Gemmer gridet i Graph objektet.

    def in_bounds(self, position): # Tjekker om positionen er inden for gridets grænser.
        x, y = position
        return 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid)

    def passable(self, position): # Returnerer True hvis positionen kan passeres, ellers False.
        x, y = position # Udtrækker x og y koordinater fra positionen.
        return self.grid[y][x].bevægelsesomkostning > 0 # Returnerer True hvis bevægelsesomkostningen er større end 0, ellers False.

    def neighbors(self, position): # Finder naboer til en given position, som er inden for grænserne og kan passeres.
        x, y = position # Udtrækker x og y koordinater fra positionen.
        results = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)] # Potentielle naboer (op, ned, venstre, højre).
        results = filter(self.in_bounds, results) # Filtrerer naboer, der er inden for gridets grænser.
        results = filter(self.passable, results) # Filtrerer naboer, der kan passeres.
        return list(results) # Returnerer listen af gyldige naboer.
    
    def cost(self, from_node, to_node): # Beregner omkostningen ved at bevæge sig fra en node til en anden.
        x0, y0 = from_node # Udtrækker x og y koordinater fra from_node.
        x1, y1 = to_node # Udtrækker x og y koordinater fra to_node.
        return self.grid[y1][x1].bevægelsesomkostning # Returnerer bevægelsesomkostningen for to_node.

graph = Graph(grid) # Opretter et Graph objekt med det givne grid.

# ----------------------------------------------------
# Funktion til at rekonstruere stien fra start til mål
# ----------------------------------------------------
def reconstruct_path(came_from, start, goal): # Rekonstruerer stien fra start til mål ved hjælp af came_from dictionary.
    if goal not in came_from: # Hvis målet ikke er i came_from, returner None.
        return None
    path, current = [], goal # Initialiserer stien og sætter current til målet.
    while current is not None: # Gennemgår came_from for at rekonstruere stien.
        path.append(current) # Tilføjer current til stien.
        current = came_from[current] # Opdaterer current til dens forælder.
    path.reverse() # Reverser stien for at starte fra start.
    return path # Returnerer den rekonstruerede sti.

# --------------------------------------
# A* som generator (ét skridt ad gangen)
# --------------------------------------
def astar_steps(graph, start, goal): # A* algoritme som generator, der returnerer ét skridt ad gangen.
    frontier = [] # Prioritetskø for noder, der skal udforskes.
    heapq.heappush(frontier, (0, 0, start)) # Tilføjer startnoden til frontier med prioritet 0 (f = g + h, hvor g = 0 og h = 0).
    came_from = {start: None} # Dictionary til at holde styr på forældre for hver node.
    cost_so_far = {start: 0} # Dictionary til at holde styr på omkostninger fra start til hver node.

    while frontier: # Så længe der er noder i frontier, fortsæt søgningen.
        _, _, current = heapq.heappop(frontier) # Henter noden med lavest prioritet fra frontier.
        yield current, came_from, frontier # Returnerer current, came_from og frontier til den kaldende kode. Så visualiseringen kan opdateres.

        if current == goal: # Hvis vi har nået målet, afslut generatoren.
            return

        for nxt in graph.neighbors(current): # Gennemgår alle naboer til current.
            new_cost = cost_so_far[current] + graph.cost(current, nxt) # Beregner den nye omkostning til naboen.
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]: # Hvis naboen ikke er besøgt eller den nye omkostning er lavere, opdater.
                cost_so_far[nxt] = new_cost # Opdaterer omkostningen for naboen.
                h = heuristic(goal, nxt) # Beregner heuristikken for naboen.
                heapq.heappush(frontier, (new_cost + h, h, nxt)) # Tilføjer naboen til frontier med prioritet baseret på omkostning + heuristik.
                came_from[nxt] = current # Opdaterer came_from for naboen.



# ------
# Pygame
# ------
CELL = 20 # Størrelsen på hver celle i pixels.
COLORS = { # Farver for forskellige terræntyper.
    "grass": (86, 170, 80),
    "water": (60, 120, 200),
    "mountain": (130, 130, 130),
    "lava": (220, 60, 30),
}
VISITED = (240, 220, 120) # Farve for besøgte celler.
FRONTIER = (255, 255, 255) # Farve for celler i frontier.
PATH = (160, 40, 200) # Farve for den fundne sti.

pygame.init() 
screen = pygame.display.set_mode((width * CELL, height * CELL)) # Opretter vinduet med størrelsen baseret på gridens dimensioner og celle-størrelsen.
pygame.display.set_caption("A* pathfinding") # Sætter vinduets titel.
clock = pygame.time.Clock() # Opretter en clock til at styre opdateringshastigheden i animationen.

def draw_cell(pos, color): # Tegner en celle på skærmen med den givne farve.
    x, y = pos # Udtrækker x- og y-koordinater fra pos.
    pygame.draw.rect(screen, color, (x * CELL, y * CELL, CELL - 1, CELL - 1)) # Tegner rektanglet for cellen på skærmen.

def draw(came_from, frontier, path, done): # Tegner hele gridet, besøgte celler, frontier og sti.
    for y in range(height): # Gennemgår alle rækker i gridet.
        for x in range(width): # Gennemgår alle kolonner i gridet.
            draw_cell((x, y), COLORS[grid[y][x].navn]) # Tegner cellen med farven baseret på terræntypen.

    if not done: # Hvis søgningen ikke er færdig, vis besøgte celler og frontier.
        for pos in came_from: # Tegner alle celler, der er blevet besøgt.
            draw_cell(pos, VISITED) # Tegner cellen som besøgt.
        for _, _, pos in frontier: # Tegner alle celler i frontier.
            draw_cell(pos, FRONTIER) # Tegner cellen som en del af frontier.
    elif path is not None: # Hvis en sti er fundet, vis kun stien.
        for pos in path: # Tegner alle celler i stien.
            draw_cell(pos, PATH) # Tegner cellen som en del af stien.

    draw_cell(start, (0, 0, 0)) # Tegner startcellen i sort for at markere startpunktet.
    draw_cell(goal, (0, 0, 0)) # Tegner målcellen i sort for at markere målet.
    pygame.display.flip() # Opdaterer skærmen med de nye tegninger.

steps = astar_steps(graph, start, goal) # Initialiserer generatoren for A* algoritmens skridt.
came_from, frontier, path = {start: None}, [], None # Initialiserer came_from, frontier og path.
done = False # Flag for at indikere om søgningen er færdig.

running = True # Flag for at holde hovedløkken kørende.
while running:
    for event in pygame.event.get(): # Håndterer alle pygame events.
        if event.type == pygame.QUIT: # Hvis brugeren lukker vinduet.
            running = False # Stop hovedløkken.

    if not done: # Hvis søgningen ikke er færdig, tag næste skridt.
        step = next(steps, None) # Hent næste skridt fra generatoren.
        if step is None: # Hvis generatoren er færdig, marker som done.
            done = True
            path = reconstruct_path(came_from, start, goal) # Rekonstruer stien.
            if path is None: # Hvis ingen sti blev fundet.
                print("Ingen sti fundet")
            else:
                total_cost = sum(graph.cost(a, b) for a, b in zip(path, path[1:])) # Beregn samlet omkostning.
                print("Sti fundet, skridt:", len(path) - 1, "samlet omkostning:", total_cost) # Udskriv information om den fundne sti.
        else: 
            current, came_from, frontier = step # Opdater current, came_from og frontier.
            if current == goal: # Hvis målet er nået.
                done = True # Marker søgningen som færdig.
                path = reconstruct_path(came_from, start, goal) # Rekonstruer stien.
                total_cost = sum(graph.cost(a, b) for a, b in zip(path, path[1:])) # Beregn samlet omkostning.
                print("Sti fundet, skridt:", len(path) - 1, "samlet omkostning:", total_cost) # Udskriv information om den fundne sti.

    draw(came_from, frontier, path, done) # Tegn den aktuelle tilstand af søgningen.
    clock.tick(300) # Sætter hastigheden for animationen; sænk tallet for langsommere animation.

pygame.quit()