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
   python database_setup.py
   ```
   This creates `monster_rpg_save.db` if it does not already exist.
   A default user `player1` will be created automatically. Use `database_setup.create_user()` to add more users.
3. Start the game:
   ```bash
   python main.py
   ```
   You will be asked whether to load a save file or start a new game.
4. To run the simple web server instead:
   ```bash
   pip install -r requirements.txt
   python webapp.py
   ```

## Project Structure

### Monsters
- `monsters/monster_class.py` &mdash; defines the `Monster` class and helper functions for experience and leveling.
- `monsters/monster_data.py` &mdash; contains predefined monster instances and the dictionary `ALL_MONSTERS` used by the game.
- `monsters/__init__.py` &mdash; exposes the monster classes and data for easier imports.

### Skills
- `skills/skills.py` &mdash; defines the `Skill` class and several example skills. The dictionary `ALL_SKILLS` stores all available skills.
- `skills/__init__.py` &mdash; an empty module used to mark the directory as a package.

### Maps
- `map_data.py` &mdash; defines the `Location` class and the dictionary `LOCATIONS` which describes available areas and how they connect. `STARTING_LOCATION_ID` indicates where the player begins.

Other notable modules include `player.py` (player data and save/load logic), `battle.py` (battle system), and `synthesis_rules.py` (monster fusion recipes).

## New Features
- Items can now be used both outside and during battle. The included potions restore HP and can turn the tide mid-fight.
- The starting village has a shop where you can buy Small Potions or even purchase a Slime companion.

## Saving
The game saves player data to `monster_rpg_save.db`. Only basic information is stored at the moment, but the structure is ready for expansion.

Enjoy exploring the world and training your monsters!
