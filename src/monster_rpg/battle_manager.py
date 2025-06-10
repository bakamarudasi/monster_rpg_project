# battle_manager.py
from .player import Player
from .database_setup import DATABASE_NAME


def handle_battle_loss(hero: Player) -> str:
    """Handle menu flow after the player loses a battle."""
    while True:
        print("\n--- GAME OVER ---")
        print("1: リトライする")
        print("2: セーブデータをロードする")
        print("3: ゲームを終了する")
        choice = input("選択: ").strip()
        if choice == "1":
            return "retry"
        elif choice == "2":
            loaded = Player.load_game(DATABASE_NAME)
            if loaded:
                hero.__dict__.update(loaded.__dict__)
            return "load"
        elif choice == "3":
            return "exit"
        else:
            print("無効な選択です。")
