"""Core Game of Life logic: grid updates, neighbor counting, and entropy.

All simulation functions are pure: they never mutate the grid they are
given and always return a new value. Boundaries are toroidal (the grid
wraps around on both axes).
"""

import math
import random
from collections import Counter
from typing import List

Grid = List[List[int]]

ALIVE = 1
DEAD = 0


def count_neighbors(x: int, y: int, grid: Grid) -> int:
    """Count the living neighbors of cell (x, y) with wrap-around edges."""
    height = len(grid)
    width = len(grid[0]) if height else 0
    total = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            ny = (y + dy) % height
            nx = (x + dx) % width
            total += grid[ny][nx]
    return total


def update_grid(current_grid: Grid) -> Grid:
    """Apply Conway's rules and return a brand new grid (input untouched)."""
    height = len(current_grid)
    width = len(current_grid[0]) if height else 0

    new_grid = [[DEAD for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            alive = current_grid[y][x] == ALIVE
            neighbors = count_neighbors(x, y, current_grid)
            if alive and neighbors in (2, 3):
                new_grid[y][x] = ALIVE
            elif not alive and neighbors == 3:
                new_grid[y][x] = ALIVE
            else:
                new_grid[y][x] = DEAD
    return new_grid


def count_living(grid: Grid) -> int:
    """Return the total number of living cells in the grid."""
    return sum(sum(row) for row in grid)


def calculate_entropy(grid: Grid) -> float:
    """Compute the Shannon entropy of the grid's 3x3 neighborhood patterns.

    Every 3x3 window (toroidal) is encoded as a 9-bit pattern; the entropy
    is calculated over the distribution of those patterns across the grid.
    """
    height = len(grid)
    width = len(grid[0]) if height else 0
    if height == 0 or width == 0:
        return 0.0

    pattern_counts: Counter = Counter()
    for y in range(height):
        for x in range(width):
            pattern = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny = (y + dy) % height
                    nx = (x + dx) % width
                    pattern = (pattern << 1) | grid[ny][nx]
            pattern_counts[pattern] += 1

    total = height * width
    entropy = 0.0
    for count in pattern_counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


def make_empty_grid(width: int, height: int) -> Grid:
    """Return a new dead grid of the given dimensions."""
    return [[DEAD for _ in range(width)] for _ in range(height)]


def make_random_grid(width: int, height: int, density: float) -> Grid:
    """Return a new grid randomly populated at the given density."""
    return [
        [ALIVE if random.random() < density else DEAD for _ in range(width)]
        for _ in range(height)
    ]


def _stamp(grid: Grid, top: int, left: int, shape: List[List[int]]) -> Grid:
    """Return a copy of grid with shape stamped at (top, left), wrapping."""
    height = len(grid)
    width = len(grid[0]) if height else 0
    new_grid = [row[:] for row in grid]
    for dy, row in enumerate(shape):
        for dx, value in enumerate(row):
            if value:
                new_grid[(top + dy) % height][(left + dx) % width] = ALIVE
    return new_grid


def make_glider_grid(width: int, height: int) -> Grid:
    """Return a new grid containing a single glider near the top-left."""
    glider = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    grid = make_empty_grid(width, height)
    return _stamp(grid, 1, 1, glider)


def make_blinker_grid(width: int, height: int) -> Grid:
    """Return a new grid containing a single blinker at the center."""
    blinker = [[1, 1, 1]]
    grid = make_empty_grid(width, height)
    return _stamp(grid, height // 2, max(width // 2 - 1, 0), blinker)


def make_block_grid(width: int, height: int) -> Grid:
    """Return a new grid containing a single still-life block at the center."""
    block = [
        [1, 1],
        [1, 1],
    ]
    grid = make_empty_grid(width, height)
    return _stamp(grid, height // 2, width // 2, block)


class SimulationState:
    """Holds the current grid plus the full, untruncated simulation history."""

    def __init__(self, width: int, height: int, density: float) -> None:
        self.width = width
        self.height = height
        self.density = density
        self.grid: Grid = make_empty_grid(width, height)
        self.generation: int = 0
        self.living_history: List[int] = []
        self.entropy_history: List[float] = []
        self.reset("clear")

    def _record(self) -> None:
        self.living_history.append(count_living(self.grid))
        self.entropy_history.append(calculate_entropy(self.grid))

    def reset(self, pattern: str) -> None:
        """Reset the grid to a named pattern, clearing all history."""
        builders = {
            "random": lambda: make_random_grid(self.width, self.height, self.density),
            "glider": lambda: make_glider_grid(self.width, self.height),
            "blinker": lambda: make_blinker_grid(self.width, self.height),
            "block": lambda: make_block_grid(self.width, self.height),
            "clear": lambda: make_empty_grid(self.width, self.height),
        }
        if pattern not in builders:
            raise ValueError(f"Unknown pattern: {pattern}")

        self.grid = builders[pattern]()
        self.generation = 0
        self.living_history = []
        self.entropy_history = []
        self._record()

    def clear(self) -> None:
        """Clear the grid to all-dead, resetting generation and history."""
        self.reset("clear")

    def step(self) -> None:
        """Advance the simulation by one generation and record history."""
        self.grid = update_grid(self.grid)
        self.generation += 1
        self._record()

    def toggle(self, x: int, y: int) -> None:
        """Toggle a single cell, resetting the generation counter and history."""
        new_grid = [row[:] for row in self.grid]
        new_grid[y][x] = DEAD if new_grid[y][x] == ALIVE else ALIVE
        self.grid = new_grid
        self.generation = 0
        self.living_history = []
        self.entropy_history = []
        self._record()

    def to_dict(self) -> dict:
        return {
            "grid": self.grid,
            "generation": self.generation,
            "living_count": self.living_history[-1] if self.living_history else 0,
            "entropy": self.entropy_history[-1] if self.entropy_history else 0.0,
            "living_history": self.living_history,
            "entropy_history": self.entropy_history,
        }
