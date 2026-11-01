# PyArcade

A small Poki-style website. Everything is Python: the games (pygame), the API (Flask) and the website (NiceGUI).

```
pyarcade/
  docker-compose.yml  render.yaml  README.md
  backend/     Flask API + the six games
    app.py  config.py  gunicorn.conf.py  requirements.txt  Dockerfile
    routes/    games.py  sessions.py  health.py
    services/  session_manager.py  game_runner.py
    games/     registry.py  snake.py  pacman.py  chess_game.py  dino_run.py  flappy_bird.py  car_racing.py
    tests/     test_api.py  fake_runner.py
  frontend/    Python website (NiceGUI)
    main.py  config.py  api_client.py  theme.py  requirements.txt  Dockerfile
    pages/     home.py  play.py
```

## How it works

```
Browser -> frontend (NiceGUI, :8080) -> HTTP -> backend (Flask API, :5000) -> starts game_runner.py <game.py>
Browser <---------- live game video (MJPEG) straight from  GET /api/sessions/<id>/stream
```

The frontend page asks the API to start a game, shows the live video, and forwards key presses / clicks to
`POST /api/sessions/<id>/input`. `game_runner.py` runs each game file unchanged with an invisible pygame window.

## API

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Server status |
| GET | `/api/games`, `/api/games/<id>` | List games / one game with its controls |
| POST | `/api/sessions` | Body `{"game_id": "snake"}`. Starts a game |
| GET | `/api/sessions/<id>` | Is the game still running? |
| GET | `/api/sessions/<id>/stream` | Live video of the game (MJPEG) |
| POST | `/api/sessions/<id>/input` | Body `{"events": [{"type": "keydown", "code": "ArrowLeft"}]}` |
| DELETE | `/api/sessions/<id>` | Stop the game (`POST .../stop` does the same) |

## Run locally (two terminals)

```
# terminal 1 - backend
cd backend
python -m pip install -r requirements.txt
python app.py                      # http://localhost:5000

# terminal 2 - frontend
cd frontend
python -m pip install -r requirements.txt
python main.py                     # http://localhost:8080  <- open this
```

Backend tests (no pygame needed): `cd backend && python -m unittest discover -s tests -t .`

## Deploy

Two services are needed: the API (`backend/`) and the website (`frontend/`).
- **Render:** push to GitHub, New > Blueprint. Then set `BACKEND_URL` and `PUBLIC_BACKEND_URL` on the website service to the API's public URL.
- **Docker anywhere:** `docker compose up --build`.
- Keep **one gunicorn worker** for the API (already set): running games live in its memory.

Settings: backend `MAX_SESSIONS`, `NO_VIEWER_TIMEOUT`, `IDLE_INPUT_TIMEOUT`, `STREAM_FPS`, `FRAME_FORMAT`, `CORS_ORIGINS`; frontend `BACKEND_URL`, `PUBLIC_BACKEND_URL`, `PORT`.

## Add a game
Put the pygame file in `backend/games/` and add one entry to `GAMES` in `backend/games/registry.py`.
