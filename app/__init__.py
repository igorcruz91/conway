"""Flask app factory for the Conway's Game of Life web application."""

from flask import Flask

from config.config import GRID_HEIGHT, GRID_WIDTH, RANDOM_DENSITY

from app.simulation import SimulationState


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)

    app.simulation = SimulationState(
        width=GRID_WIDTH, height=GRID_HEIGHT, density=RANDOM_DENSITY
    )

    from app.routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app
