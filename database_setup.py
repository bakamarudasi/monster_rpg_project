# database_setup.py (新規作成)
import sqlite3

DATABASE_NAME = "monster_rpg_save.db"


def _ensure_default_user(cursor):
    """Create a default user account if no users exist."""
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("player1", "password"),
        )

def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # users テーブルの作成
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    # player_data テーブルの作成 (存在しなければ)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS player_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            player_level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            current_location_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    # 当面は1プレイヤーなので、player_dataテーブルには1行だけ入る想定
    # (あるいはid=1の行だけを常に使うなど)

    # party_monsters テーブルの作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS party_monsters (
        player_id INTEGER,
        monster_id TEXT,
        level INTEGER,
        exp INTEGER
    )
    """)

    # player_items テーブルの作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_items (
        player_id INTEGER,
        item_id TEXT
    )
    """)

    _ensure_default_user(cursor)

    conn.commit()
    conn.close()
    print("データベースの初期化が完了しました (または既に初期化済みです)。")


def create_user(username: str, password: str) -> int:
    """Create a new user and return its ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_id(username: str) -> int | None:
    """Return user id for given username, or None if not found."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

if __name__ == '__main__':
    # このファイルを直接実行した場合、データベースを初期化する
    initialize_database()
