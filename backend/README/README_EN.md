# Monster RPG

This is a small text-based RPG prototype written in Python. It uses SQLite to store simple save data and now supports multiple user accounts. A minimal Flask web server is also included.

> **Note**
> The `docker-compose.yml` file simply launches the Flask backend and no longer includes a PostgreSQL service. The game continues to use the local SQLite database `monster_rpg_save.db`.

## Requirements
- Python 3.11
- `Flask` is required to run the optional web server.
- The standard library `sqlite3` module is used for save data.

## Setup and Running the Game
1. (Optional) Create and activate a virtual environment for Python 3.11.
2. Install the package in editable mode and initialize the SQLite database:
   ```bash
   pip install -e .
   python -m monster_rpg.database_setup
   ```
   This creates `monster_rpg_save.db` if it does not already exist.
   Set the `MONSTER_RPG_DB` environment variable to use a different
   location for the SQLite save file.
   A default user `player1` will be created automatically. Use `database_setup.create_user()` to add more users.
3. To run the simple web server instead:
   ```bash
   pip install -r requirements.txt
   python -m monster_rpg.webapp
   ```
   `webapp.py` exposes only a couple JSON endpoints (like `/new_game` and
   `/load_game`) and does not include the battle system.
4. Another web interface exists. Use the provided launcher script:
  ```bash
   pip install -r requirements.txt
   python -m monster_rpg.start_rpg
   ```
   This starts the server at <http://localhost:5000/> using Flask templates
   and provides the full game including battles.
   Set the `FLASK_SECRET_KEY` environment variable to customize the
   Flask secret key (defaults to `dev-secret`).

## Running with Docker

The repository includes a `docker-compose.yml` that starts the Flask backend using SQLite. Build the image and launch the container:

```bash
docker-compose build
docker-compose up
```

The backend service exposes port 5000 and mounts `./backend/src` into the container so code changes are reflected immediately.

## Project Structure

### Monsters
- `monsters/monster_class.py` &mdash; defines the `Monster` class and helper functions for experience and leveling.
- `monsters/monster_data.py` &mdash; contains predefined monster instances and the dictionary `ALL_MONSTERS` used by the game.
- `monsters/__init__.py` &mdash; exposes the monster classes and data for easier imports.

Use `monster_loader.load_monsters()` to read monster definitions from `monsters/monsters.json`. A `ValueError` is raised if the file is missing or contains invalid JSON.

### Skills and Items
- `skills/skills.py` &mdash; defines the `Skill` class and loads definitions from `skills/skills.json`. The dictionary `ALL_SKILLS` stores all available skills.
- `items/item_data.py` &mdash; defines the `Item` class and loads data from `items/items.json` as `ALL_ITEMS`.
- `skills/__init__.py` &mdash; an empty module used to mark the directory as a package.
- `skills/skill_sets.py` &mdash; loads reusable skill packages defined in `skills/skill_sets.json`.

#### Skill Sets
`skill_sets.json` groups common learnsets that multiple monsters can reference. Each entry is keyed by an identifier and contains a display `name` and a `learnset` dictionary mapping a level to one or more skill IDs.

```json
{
  "starter_slime": {
    "name": "Slime Basics",
    "learnset": {
      "1": ["heal"],
      "2": ["guard_up"]
    }
  }
}
```

Monsters may include a `skill_sets` array and an optional `additional_skills` list inside `monsters.json`. Learnsets from these sets are merged with the monster's own `learnset`.

```json
{
  "slime": {
    "skill_sets": ["starter_slime"],
    "additional_skills": ["tackle"],
    "learnset": { "5": ["water_blast"] }
  }
}
```

In this example the Slime will start with the skills from the `starter_slime` set plus `tackle`, and will learn both the set's moves and `water_blast` as it levels.

### Maps
- `map_data.py` &mdash; defines the `Location` class and the dictionary `LOCATIONS` which describes available areas and how they connect. `STARTING_LOCATION_ID` indicates where the player begins. Locations can include an `enemy_pool` dict for weighted encounters, a `party_size` range for the number of enemies, and an optional `required_item` field to lock certain areas until the player has that item.

Example weighted enemy pool:

```json
{
  "enemy_pool": { "slime": 70, "goblin": 30 },
  "party_size": [1, 2]
}
```
Example location requiring an item:
```json
{
  "required_item": "celestial_feather",
  "connections": { "Outer": "sky_isle" }
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
- A unified `/synthesize_action/<user_id>` API now handles monster–monster,
  monster–item, and item–item fusion. The synthesis page located at
  `/synthesize/<user_id>` uses a modal dialog that posts to this endpoint.
  Both routes accept the same JSON payload so manual requests can target either
  path.
- The web interface provides a battle log page showing the results of your last fight.
- A dedicated login form lets you authenticate with your username and password.
- Monster HP and MP are now stored when you save so battles can resume exactly
  where you left off.

## Saving
The game saves player data to `monster_rpg_save.db` by default. You can
override the filename by setting the `MONSTER_RPG_DB` environment variable.
Monster HP/MP values now persist across sessions. If you upgrade the game, run
`python -m monster_rpg.database_setup` again (or call
`database_setup.initialize_database()` in code) to add any new columns and
tables, such as the HP/MP fields or the `exploration_progress` table, to
existing save files.

## Monster Images
Place monster pictures under `src/monster_rpg/static/images/` on your local machine. The folder is kept in the repository via an empty `.gitkeep` file but ignored by Git so large image files do not get uploaded.
The game does **not** include any monster artwork. You must supply PNG files whose names match the `image_filename` entries in `monsters/monster_data.py`. Example files are `slime.png` and `wolf.png`.

## Building Tailwind CSS
Run the Tailwind CLI whenever you modify `tailwind_src.css` to regenerate the compiled stylesheet:

```bash
npx tailwindcss -i src/monster_rpg/static/tailwind_src.css -o src/monster_rpg/static/tailwind.css
```

## Testing
The tests rely on the project being installed. **Always** install the package in
editable mode before running `pytest` or the imports will fail:

```bash
pip install -e .
pytest
```

You can also run `make test` to perform both steps automatically.

Enjoy exploring the world and training your monsters!

## License
This project is licensed under the [MIT License](../LICENSE).
