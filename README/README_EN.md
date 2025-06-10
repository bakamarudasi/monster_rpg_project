# Monster RPG

This is a small text-based RPG prototype written in Python. It uses SQLite to store simple save data and now supports multiple user accounts. A minimal Flask web server is also included.

## Requirements
- Python 3 (tested with Python 3.11)
- `Flask` is required to run the optional web server.
- The standard library `sqlite3` module is used for save data.

## Setup and Running the Game
1. (Optional) Create and activate a virtual environment for Python 3.
2. Initialize the SQLite database by running:
   ```bash
   python -m monster_rpg.database_setup
   ```
   This creates `monster_rpg_save.db` if it does not already exist.
   A default user `player1` will be created automatically. Use `database_setup.create_user()` to add more users.
3. (Optional) Run the classic CLI version:
   ```bash
   python -m monster_rpg.old_cli.main
   ```
   This older interface will ask whether to load a save file or start a new game.
4. To run the simple web server instead:
   ```bash
   pip install -r requirements.txt
   python -m monster_rpg.webapp
   ```
   `webapp.py` exposes only a couple JSON endpoints (like `/new_game` and
   `/load_game`) and does not include the battle system.
5. Another web interface exists. Use the provided launcher script:
   ```bash
   pip install -r requirements.txt
   python -m monster_rpg.start_rpg
   ```
   This starts the server at <http://localhost:5000/> using Flask templates
   and provides the full game including battles.

## Project Structure

### Monsters
- `monsters/monster_class.py` &mdash; defines the `Monster` class and helper functions for experience and leveling.
- `monsters/monster_data.py` &mdash; contains predefined monster instances and the dictionary `ALL_MONSTERS` used by the game.
- `monsters/__init__.py` &mdash; exposes the monster classes and data for easier imports.

### Skills
- `skills/skills.py` &mdash; defines the `Skill` class and several example skills. The dictionary `ALL_SKILLS` stores all available skills.
- `skills/__init__.py` &mdash; an empty module used to mark the directory as a package.

### Maps
- `map_data.py` &mdash; defines the `Location` class and the dictionary `LOCATIONS` which describes available areas and how they connect. `STARTING_LOCATION_ID` indicates where the player begins. Locations can include an `enemy_pool` dict for weighted encounters and a `party_size` range for the number of enemies.

Example weighted enemy pool:

```json
{
  "enemy_pool": { "slime": 70, "goblin": 30 },
  "party_size": [1, 2]
}
```

Other notable modules include `player.py` (player data and save/load logic), `battle.py` (battle system), and `monsters/synthesis_rules.py` (monster fusion recipes).

## New Features
- Items can now be used both outside and during battle. The included potions restore HP and can turn the tide mid-fight.
- The starting village has a shop where you can buy Small Potions or even purchase a Slime companion.
- Defeated monsters may drop items, which are automatically added to your inventory.
- Basic equipment crafting has been added. Use collected items to craft simple weapons and armor.
- Some monsters now evolve once they reach certain levels.
- Monsters can also be fused with special items to create entirely new creatures.
- The web interface provides a battle log page showing the results of your last fight.
- A dedicated login form lets you authenticate with your username and password.

## Saving
The game saves player data to `monster_rpg_save.db`. Only basic information is stored at the moment, but the structure is ready for expansion.

## Monster Images
Place monster pictures under `static/images/` on your local machine. The folder is kept in the repository via an empty `.gitkeep` file but ignored by Git so large image files do not get uploaded.

Enjoy exploring the world and training your monsters!

## License
This project is licensed under the [MIT License](../LICENSE).
