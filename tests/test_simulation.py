"""Unit tests for the core Game of Life simulation logic."""

import math

from app.simulation import (
    SimulationState,
    calculate_entropy,
    count_living,
    count_neighbors,
    make_block_grid,
    make_blinker_grid,
    make_empty_grid,
    make_glider_grid,
    update_grid,
)


def test_count_neighbors_center_cell():
    grid = [
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
    ]
    assert count_neighbors(1, 1, grid) == 3


def test_count_neighbors_wraps_around_edges():
    grid = [
        [1, 0, 1],
        [0, 0, 0],
        [1, 0, 1],
    ]
    # Corner (0, 0) neighbors wrap to the opposite edges of the grid.
    assert count_neighbors(0, 0, grid) == 3


def test_update_grid_does_not_mutate_input():
    grid = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
    ]
    original = [row[:] for row in grid]
    update_grid(grid)
    assert grid == original


def test_blinker_oscillates_with_period_two():
    grid = make_blinker_grid(5, 5)
    first_step = update_grid(grid)
    second_step = update_grid(first_step)
    assert second_step == grid


def test_block_is_a_still_life():
    grid = make_block_grid(5, 5)
    next_step = update_grid(grid)
    assert next_step == grid


def test_glider_preserves_population_after_one_step():
    grid = make_glider_grid(8, 8)
    next_step = update_grid(grid)
    assert count_living(next_step) == count_living(grid) == 5


def test_underpopulation_kills_isolated_cell():
    grid = make_empty_grid(3, 3)
    grid[1][1] = 1
    next_step = update_grid(grid)
    assert count_living(next_step) == 0


def test_overpopulation_kills_crowded_cell():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ]
    next_step = update_grid(grid)
    assert next_step[1][1] == 0


def test_reproduction_births_new_cell():
    grid = [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ]
    next_step = update_grid(grid)
    assert next_step[0][1] == 1
    assert next_step[2][1] == 1


def test_entropy_of_empty_grid_is_zero():
    grid = make_empty_grid(4, 4)
    assert calculate_entropy(grid) == 0.0


def test_entropy_is_deterministic():
    grid = make_glider_grid(6, 6)
    assert calculate_entropy(grid) == calculate_entropy(grid)


def test_entropy_is_nonnegative_and_finite():
    grid = make_glider_grid(6, 6)
    entropy = calculate_entropy(grid)
    assert entropy >= 0.0
    assert math.isfinite(entropy)


def test_simulation_state_reset_clears_history():
    state = SimulationState(width=10, height=10, density=0.3)
    state.step()
    state.step()
    assert state.generation == 2
    state.reset("blinker")
    assert state.generation == 0
    assert state.living_history == [count_living(state.grid)]
    assert state.entropy_history == [calculate_entropy(state.grid)]


def test_simulation_state_step_appends_history_without_truncation():
    state = SimulationState(width=6, height=6, density=0.3)
    state.reset("glider")
    for _ in range(20):
        state.step()
    assert len(state.living_history) == 21
    assert len(state.entropy_history) == 21


def test_simulation_state_toggle_flips_cell_and_resets_generation():
    state = SimulationState(width=5, height=5, density=0.0)
    state.reset("clear")
    assert state.grid[2][2] == 0
    state.step()
    state.toggle(2, 2)
    assert state.grid[2][2] == 1
    assert state.generation == 0
