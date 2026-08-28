# Conway's Game of Life

Uma implementação web do Jogo da Vida de Conway, com backend em Flask e
frontend em Canvas + Chart.js.

## Arquitetura

- `app/simulation.py` — lógica pura da simulação: `count_neighbors`,
  `update_grid`, `calculate_entropy`, e a classe `SimulationState` que mantém
  a grade atual e o histórico completo (`living_history`, `entropy_history`).
- `app/routes.py` — endpoints da API (`/api/state`, `/api/step`,
  `/api/reset/<pattern>`, `/api/clear`, `/api/toggle`).
- `app/templates/index.html` — página principal.
- `app/static/js/main.js` — renderização do grid em `<canvas>`, clique para
  alternar células, e gráficos de histórico (Chart.js).
- `app/static/css/style.css` — estilos.
- `config/config.py` — tamanho da grade, intervalo de atualização, densidade
  do preenchimento aleatório.
- `tests/` — testes pytest para a lógica de simulação e para a API.

## Configuração

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Executando

```bash
python run.py
```

A aplicação fica disponível em `http://127.0.0.1:5000`.

Por padrão o modo debug do Flask fica desligado. Para ativá-lo em desenvolvimento
local (nunca em produção — o debugger interativo permite execução remota de
código), defina `FLASK_DEBUG=1` antes de rodar:

```bash
set FLASK_DEBUG=1   # Windows
python run.py
```

## Testes

```bash
pytest
```

## Formatação e lint

```bash
black .
flake8
```

## API

| Método | Rota                  | Descrição                                   |
|--------|------------------------|----------------------------------------------|
| GET    | `/api/state`           | Retorna grade atual, métricas e histórico completo |
| POST   | `/api/step`            | Avança uma geração                            |
| POST   | `/api/reset/<pattern>` | Reinicia com um padrão (`random`, `glider`, `blinker`, `block`, `clear`) |
| POST   | `/api/clear`           | Limpa a grade                                 |
| POST   | `/api/toggle`          | Alterna a célula em `{x, y}`                  |

## Regras da simulação

- Grade toroidal (bordas conectadas).
- `update_grid` é pura: nunca modifica a grade recebida, sempre retorna uma nova.
- Entropia de Shannon calculada sobre os padrões 3x3 de cada célula.
- O histórico de população e entropia é armazenado por completo, sem truncamento,
  e é reiniciado sempre que a grade é resetada ou uma célula é alternada manualmente.
