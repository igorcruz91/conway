"""Integration tests for the Game of Life API endpoints."""

import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_get_state_returns_grid_and_history(client):
    response = client.get("/api/state")
    data = response.get_json()
    assert response.status_code == 200
    assert "grid" in data
    assert "living_history" in data
    assert "entropy_history" in data
    assert data["generation"] == 0


def test_step_advances_generation(client):
    response = client.post("/api/step")
    data = response.get_json()
    assert response.status_code == 200
    assert data["generation"] == 1
    assert len(data["living_history"]) == 2


def test_reset_to_glider(client):
    response = client.post("/api/reset/glider")
    data = response.get_json()
    assert response.status_code == 200
    assert data["generation"] == 0
    assert data["living_count"] == 5


def test_reset_with_invalid_pattern_returns_400(client):
    response = client.post("/api/reset/not-a-pattern")
    assert response.status_code == 400


def test_clear_empties_the_grid(client):
    client.post("/api/reset/glider")
    response = client.post("/api/clear")
    data = response.get_json()
    assert response.status_code == 200
    assert data["living_count"] == 0


def test_toggle_flips_a_cell(client):
    client.post("/api/clear")
    response = client.post("/api/toggle", json={"x": 3, "y": 4})
    data = response.get_json()
    assert response.status_code == 200
    assert data["grid"][4][3] == 1
    assert data["generation"] == 0


def test_toggle_out_of_bounds_returns_400(client):
    response = client.post("/api/toggle", json={"x": 9999, "y": 9999})
    assert response.status_code == 400


def test_toggle_missing_fields_returns_400(client):
    response = client.post("/api/toggle", json={})
    assert response.status_code == 400
