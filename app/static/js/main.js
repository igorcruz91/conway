(() => {
    "use strict";

    const { gridWidth, gridHeight, updateIntervalMs } = window.CONWAY_CONFIG;
    const CELL_SIZE = 16;
    const GAP = 1;

    const canvas = document.getElementById("grid-canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = gridWidth * CELL_SIZE;
    canvas.height = gridHeight * CELL_SIZE;

    const playPauseBtn = document.getElementById("play-pause-btn");
    const stepBtn = document.getElementById("step-btn");
    const clearBtn = document.getElementById("clear-btn");
    const resetBtn = document.getElementById("reset-btn");
    const patternSelect = document.getElementById("pattern-select");
    const generationValue = document.getElementById("generation-value");
    const livingValue = document.getElementById("living-value");
    const entropyValue = document.getElementById("entropy-value");

    let playing = false;
    let timerId = null;
    let lastGrid = null;

    const livingChart = new Chart(document.getElementById("living-chart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Células vivas",
                data: [],
                borderColor: "#5ac8fa",
                backgroundColor: "rgba(90, 200, 250, 0.15)",
                tension: 0.2,
                pointRadius: 0,
            }],
        },
        options: {
            animation: false,
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Geração" } },
                y: { beginAtZero: true },
            },
        },
    });

    const entropyChart = new Chart(document.getElementById("entropy-chart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Entropia (bits)",
                data: [],
                borderColor: "#ff9f43",
                backgroundColor: "rgba(255, 159, 67, 0.15)",
                tension: 0.2,
                pointRadius: 0,
            }],
        },
        options: {
            animation: false,
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Geração" } },
                y: { beginAtZero: true },
            },
        },
    });

    function drawGrid(grid) {
        lastGrid = grid;
        ctx.fillStyle = "#1a1d29";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#5ac8fa";
        for (let y = 0; y < grid.length; y += 1) {
            for (let x = 0; x < grid[y].length; x += 1) {
                if (grid[y][x] === 1) {
                    ctx.fillRect(
                        x * CELL_SIZE + GAP,
                        y * CELL_SIZE + GAP,
                        CELL_SIZE - GAP,
                        CELL_SIZE - GAP
                    );
                }
            }
        }
    }

    function updateMetrics(state) {
        generationValue.textContent = state.generation;
        livingValue.textContent = state.living_count;
        entropyValue.textContent = state.entropy.toFixed(2);
    }

    function updateCharts(state) {
        const labels = state.living_history.map((_, i) => i);
        livingChart.data.labels = labels;
        livingChart.data.datasets[0].data = state.living_history;
        livingChart.update("none");

        entropyChart.data.labels = labels;
        entropyChart.data.datasets[0].data = state.entropy_history;
        entropyChart.update("none");
    }

    function applyState(state) {
        drawGrid(state.grid);
        updateMetrics(state);
        updateCharts(state);
    }

    async function fetchState() {
        const response = await fetch("/api/state");
        return response.json();
    }

    async function step() {
        const response = await fetch("/api/step", { method: "POST" });
        return response.json();
    }

    async function resetPattern(pattern) {
        const response = await fetch(`/api/reset/${pattern}`, { method: "POST" });
        return response.json();
    }

    async function clearGrid() {
        const response = await fetch("/api/clear", { method: "POST" });
        return response.json();
    }

    async function toggleCell(x, y) {
        const response = await fetch("/api/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ x, y }),
        });
        return response.json();
    }

    function stopPlaying() {
        playing = false;
        playPauseBtn.textContent = "Iniciar";
        if (timerId !== null) {
            clearInterval(timerId);
            timerId = null;
        }
    }

    function startPlaying() {
        playing = true;
        playPauseBtn.textContent = "Pausar";
        timerId = setInterval(async () => {
            const state = await step();
            applyState(state);
        }, updateIntervalMs);
    }

    playPauseBtn.addEventListener("click", () => {
        if (playing) {
            stopPlaying();
        } else {
            startPlaying();
        }
    });

    stepBtn.addEventListener("click", async () => {
        const state = await step();
        applyState(state);
    });

    clearBtn.addEventListener("click", async () => {
        stopPlaying();
        const state = await clearGrid();
        applyState(state);
    });

    resetBtn.addEventListener("click", async () => {
        stopPlaying();
        const state = await resetPattern(patternSelect.value);
        applyState(state);
    });

    canvas.addEventListener("click", async (event) => {
        if (!lastGrid) return;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = Math.floor(((event.clientX - rect.left) * scaleX) / CELL_SIZE);
        const y = Math.floor(((event.clientY - rect.top) * scaleY) / CELL_SIZE);
        if (x < 0 || y < 0 || x >= gridWidth || y >= gridHeight) return;

        stopPlaying();
        const state = await toggleCell(x, y);
        applyState(state);
    });

    (async () => {
        const state = await fetchState();
        applyState(state);
    })();
})();
