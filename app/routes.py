"""API endpoints and main view for the Game of Life application."""

from flask import Blueprint, current_app, jsonify, render_template, request

from config.config import GRID_HEIGHT, GRID_WIDTH, UPDATE_INTERVAL_MS

bp = Blueprint("routes", __name__)

VALID_PATTERNS = {"random", "glider", "blinker", "block", "clear"}


@bp.route("/")
def index():
    """Render the main simulation page."""
    return render_template(
        "index.html",
        grid_width=GRID_WIDTH,
        grid_height=GRID_HEIGHT,
        update_interval_ms=UPDATE_INTERVAL_MS,
    )


@bp.route("/api/state", methods=["GET"])
def get_state():
    """Return the current grid, metrics, and full history."""
    return jsonify(current_app.simulation.to_dict())


@bp.route("/api/step", methods=["POST"])
def step():
    """Advance the simulation by one generation."""
    current_app.simulation.step()
    return jsonify(current_app.simulation.to_dict())


@bp.route("/api/reset/<pattern>", methods=["POST"])
def reset(pattern: str):
    """Reset the grid to a predefined pattern."""
    if pattern not in VALID_PATTERNS:
        return jsonify({"error": f"Unknown pattern: {pattern}"}), 400
    current_app.simulation.reset(pattern)
    return jsonify(current_app.simulation.to_dict())


@bp.route("/api/clear", methods=["POST"])
def clear():
    """Clear the grid to all-dead cells."""
    current_app.simulation.clear()
    return jsonify(current_app.simulation.to_dict())


@bp.route("/api/toggle", methods=["POST"])
def toggle():
    """Toggle a single cell at the given (x, y) coordinates."""
    payload = request.get_json(silent=True) or {}
    try:
        x = int(payload["x"])
        y = int(payload["y"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Request body must include integer x and y"}), 400

    sim = current_app.simulation
    if not (0 <= x < sim.width and 0 <= y < sim.height):
        return jsonify({"error": "Coordinates out of bounds"}), 400

    sim.toggle(x, y)
    return jsonify(sim.to_dict())
