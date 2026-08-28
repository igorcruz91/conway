# Project: Conway's Game of Life Simulation

Im using Windows. The following is an example of a project architecture.

## Development Standards
- **Language**: Python 3.9+ (backend), JavaScript ES6+ (frontend)
- **Code Style**: 
  - Python: Follow PEP 8, use Black for automatic formatting
  - JavaScript: Use Prettier or ESLint (recommended)
- **Type Hints**: Required for all Python function signatures and class definitions
- **Documentation**: 
  - Docstrings required for all public functions and classes (Python)
  - Inline comments for complex logic in both Python and JavaScript
  - Maintain a `README.md` with setup, usage, and architecture overview

## Workflow Requirements
1. Create a feature branch: `feature/[description]` or `fix/[description]`
2. Write unit tests for critical simulation logic (e.g., update_grid, count_neighbors, entropy)
3. Run `pytest` and ensure all tests pass before committing
4. Run `black .` and `flake8` on Python code; format JavaScript with Prettier
5. Update the main documentation if adding new features or changing APIs
6. Test the application manually in the browser (Chrome/Firefox) for visual regressions

## Project Structure
- `/app`: Main application package
  - `/app/__init__.py`: Flask app factory or initialization
  - `/app/routes.py`: API endpoints (state, step, reset, toggle)
  - `/app/simulation.py`: Core Game of Life logic (grid updates, neighbor counting, entropy)
  - `/app/static`: Static assets (CSS, client-side JavaScript)
  - `/app/templates`: HTML templates (Jinja2)
- `/tests`: Unit tests (pytest) for simulation logic and API endpoints
- `/config`: Configuration files (e.g., grid size, update interval, density)
- `/docs`: Additional documentation, architecture diagrams, and user guides
- `requirements.txt`: Python dependencies
- `run.py`: Entry point to start the Flask server (or use `flask run`)

## Simulation Logic Standards
- **Grid representation**: Use a 2D list of integers (0=dead, 1=alive) – *immutable when passed to functions*
- **Neighbor counting**: Must handle toroidal (wrap-around) boundaries; implement in a pure function `count_neighbors(x, y, grid)`
- **Update function**: `update_grid(current_grid)` returns a new grid; no mutation of input
- **Entropy calculation**: Compute Shannon entropy over 3×3 patterns; keep implementation deterministic and pure
- **History tracking**:
  - Store *all* generations without truncation for both living cell count and entropy
  - History lists are global to the simulation state; use `living_history` and `entropy_history`
- **State management**: Provide functions to reset the grid (random, glider, blinker, block, clear) that clear history and record generation 0

## Frontend/Visualization Guidelines
- **Backend**: Flask serves the main HTML template and JSON API endpoints
- **Frontend**:
  - Use Chart.js (v4+) for rendering living-cell and entropy history graphs
  - Canvas for the grid; each cell drawn as a rectangle with a 1‑px gap
  - Clicking a cell toggles its state (resets generation and history)
- **API Design**:
  - `GET /api/state` → returns current grid, metrics, and full history
  - `POST /api/step` → advances one generation, returns updated state and history
  - `POST /api/reset/{pattern}` → resets to a predefined pattern
  - `POST /api/clear` → clears the grid
  - `POST /api/toggle` → toggles a cell at given (x, y)
- **Performance**: Limit canvas updates to the update interval; avoid blocking the main thread

## Dependencies
- **Backend**:
  - Flask (web framework)
  - (Optional) python-dotenv for environment variable management
- **Frontend** (loaded via CDN):
  - Chart.js (for interactive graphs)
- **Testing**:
  - pytest, pytest-cov (for coverage)
  - (Optional) requests for API testing
- **Development**:
  - Black, flake8 (Python linting/formatting)
  - Prettier, ESLint (JavaScript)

## Running the Application
1. Clone the repository and set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows