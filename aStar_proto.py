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
        super().__init__("grass", 1)

class Vand(Terræn):
    def __init__(self):
        super().__init__("water", 2)

class Bjerg(Terræn):
    def __init__(self):
        super().__init__("mountain", 3)

class Lava(Terræn):
    def __init__(self):
        super().__init__("lava", None)

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
seed = random.randint(0, 100000)
print("Seed:", seed)          # så du kan genskabe et kort, du kan lide
noise = PerlinNoise(octaves=4, seed=seed)
raw = [[noise([x/width, y/height]) for x in range(width)]
       for y in range(height)]
# Beregn Perlin noise-værdien for hver celle i terrænet.


# -------------------------------
# Normaliser Perlin noise værdier
# -------------------------------
low = min(map(min, raw))
high = max(map(max, raw))
raw = [[(v - low) / (high - low) for v in row] for row in raw]   # <-- den mangler
'''low er den laveste Perlin noise værdi i terrænet.
high er den højeste Perlin noise værdi i terrænet.
Funktionerne min og max bruges til at finde den laveste og højeste Perlin noise værdi i terrænet.'''

# -------------------------------------------------------------
# Funktion til at bestemme terræn baseret på Perlin noise værdi
# -------------------------------------------------------------
def terrain(value):
    if value < 0.35:
        return VAND
    elif value < 0.65:
        return GRÆS
    elif value < 0.85:
        return BJERG
    else:
        return LAVA

# ------------------------------------
# Generer grid baseret på Perlin noise
# ------------------------------------
grid = [[terrain(value) for value in row] for row in raw]


# ---------------------------------------
# Definere start og mål for A* algoritmen
# ---------------------------------------
start = (0, 0)
goal = (width-1, height-1)
'''Jeg minusser 1 fra width og height for at få den sidste celle som mål.
Jeg gør det da jeg gerne vil have at målet er den celle i nederste højre hjørne af gridet.'''

# ------------------------------------
# Heuristik funktion til A* algoritmen
# ------------------------------------
def heuristic(a,b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# -------------------------------
# Graph klassen til A* algoritmen
# -------------------------------
class Graph:
    def __init__(self, grid):
        self.grid = grid

    # Tjekker om positionen er inden for gridets grænser
    def in_bounds(self, position):
        x, y = position
        return 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid)

    # Tjekker om positionen kan passeres (bevægelsesomkostning > 0)
    def passable(self, position):
        x, y = position
        return self.grid[y][x].bevægelsesomkostning

    # Finder naboer til en given position, som er inden for grænserne og kan passeres
    def neighbors(self, position):
        x, y = position
        results = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return list(results)
    
    # Beregner omkostningen ved at bevæge sig fra en node til en anden
    def cost(self, from_node, to_node):
        x0, y0 = from_node
        x1, y1 = to_node
        return self.grid[y1][x1].bevægelsesomkostning

graph = Graph(grid)

# ----------------------------------------------------
# Funktion til at rekonstruere stien fra start til mål
# ----------------------------------------------------
def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return None
    path, current = [], goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# ---------------------------
# A* som generator (ét skridt ad gangen)
# ---------------------------
def astar_steps(graph, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, 0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, _, current = heapq.heappop(frontier)
        yield current, came_from, frontier

        if current == goal:
            return

        for nxt in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, nxt)
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                h = heuristic(goal, nxt)
                heapq.heappush(frontier, (new_cost + h, h, nxt))
                came_from[nxt] = current

# ---------------------------
# Pygame
# ---------------------------
CELL = 20
COLORS = {
    "grass": (86, 170, 80),
    "water": (60, 120, 200),
    "mountain": (130, 130, 130),
    "lava": (220, 60, 30),
}
VISITED = (240, 220, 120)
FRONTIER = (255, 255, 255)
PATH = (160, 40, 200)

pygame.init()
screen = pygame.display.set_mode((width * CELL, height * CELL))
pygame.display.set_caption("A* pathfinding")
clock = pygame.time.Clock()

def draw_cell(pos, color):
    x, y = pos
    pygame.draw.rect(screen, color, (x * CELL, y * CELL, CELL - 1, CELL - 1))

def draw(came_from, frontier, path, done):
    for y in range(height):
        for x in range(width):
            draw_cell((x, y), COLORS[grid[y][x].navn])

    if not done:                           # kun mens søgningen kører
        for pos in came_from:
            draw_cell(pos, VISITED)
        for _, _, pos in frontier:
            draw_cell(pos, FRONTIER)
    elif path is not None:                # sti fundet: vis kun stien
        for pos in path:
            draw_cell(pos, PATH)

    draw_cell(start, (0, 0, 0))
    draw_cell(goal, (0, 0, 0))
    pygame.display.flip()

steps = astar_steps(graph, start, goal)
came_from, frontier, path = {start: None}, [], None
done = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not done:
        step = next(steps, None)
        if step is None:
            done = True
            path = reconstruct_path(came_from, start, goal)
            if path is None:
                print("Ingen sti fundet")
            else:
                total_cost = sum(graph.cost(a, b) for a, b in zip(path, path[1:]))
                print("Sti fundet, skridt:", len(path) - 1, "samlet omkostning:", total_cost)
        else:
            current, came_from, frontier = step
            if current == goal:
                done = True
                path = reconstruct_path(came_from, start, goal)
                total_cost = sum(graph.cost(a, b) for a, b in zip(path, path[1:]))
                print("Sti fundet, skridt:", len(path) - 1, "samlet omkostning:", total_cost)

    draw(came_from, frontier, path, done)
    clock.tick(300)   # sænk tallet for langsommere animation

pygame.quit()