# Monster RPG

This repository provides README files in multiple languages:

- [English](backend/README/README_EN.md)
- [日本語](backend/README/README_JA.md)

Set the environment variable `MONSTER_RPG_DB` to change where the game saves
its SQLite database.

## Quickstart
Install the package from the `backend` directory and launch the web interface:

```bash
cd backend
pip install -e .
python -m monster_rpg.database_setup
python -m monster_rpg.start_rpg
```

The server starts at <http://localhost:5000/> and provides the full game.
