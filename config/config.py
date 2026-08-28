"""Configuration values for the Conway's Game of Life simulation."""

from typing import Final

# Grid dimensions (columns x rows)
GRID_WIDTH: Final[int] = 40
GRID_HEIGHT: Final[int] = 30

# Client-side update interval, in milliseconds, between generations
UPDATE_INTERVAL_MS: Final[int] = 200

# Probability that a cell is alive when the grid is randomized
RANDOM_DENSITY: Final[float] = 0.3
