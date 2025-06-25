"""Convenience script to launch the Monster RPG web interface."""

import os
from .web_main import app

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
