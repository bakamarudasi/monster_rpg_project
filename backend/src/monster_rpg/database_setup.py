# database_setup.py (新規作成)
import os
import sqlite3
import hashlib

DATABASE_NAME = os.getenv("MONSTER_RPG_DB", "monster_rpg_save.db")


def _hash_password(password: str) -> str:
    """Return a SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _ensure_default_user(cursor):
    """Create a default user account if no users exist."""
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("player1", _hash_password("password")),
        )

def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    def _add_column_if_missing(table: str, column: str, col_type: str) -> None:
        """Add a column to a table if it does not already exist."""
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor.fetchall()]
        if column not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

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
        exp INTEGER,
        hp INTEGER,
        max_hp INTEGER,
        mp INTEGER,
        max_mp INTEGER
    )
    """)

    # 控えモンスターを保存するテーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storage_monsters (
        player_id INTEGER,
        monster_id TEXT,
        level INTEGER,
        exp INTEGER,
        hp INTEGER,
        max_hp INTEGER,
        mp INTEGER,
        max_mp INTEGER
    )
    """)

    # player_items テーブルの作成
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_items (
        player_id INTEGER,
        item_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_equipment (
        player_id INTEGER,
        equip_id TEXT,
        title_id TEXT,
        instance_id TEXT
    )
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS monster_book_status (
            player_id INTEGER,
            monster_id TEXT,
            seen INTEGER,
            captured INTEGER,
            PRIMARY KEY(player_id, monster_id)
        )
        """
    )

    # Migrate existing databases to include HP/MP columns
    for table in ("party_monsters", "storage_monsters"):
        _add_column_if_missing(table, "hp", "INTEGER")
        _add_column_if_missing(table, "max_hp", "INTEGER")
        _add_column_if_missing(table, "mp", "INTEGER")
        _add_column_if_missing(table, "max_mp", "INTEGER")

    # exploration_progress テーブルの作成
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exploration_progress (
            player_id INTEGER,
            location_id TEXT,
            progress INTEGER,
            PRIMARY KEY(player_id, location_id)
        )
        """
    )

    _ensure_default_user(cursor)

    conn.commit()
    conn.close()
    print("データベースの初期化が完了しました (または既に初期化済みです)。")


def create_user(username: str, password: str) -> int:
    """Create a new user and return its ID."""
    # Use a context manager and provide a timeout to avoid locking issues when
    # multiple requests write to the database simultaneously.
    with sqlite3.connect(DATABASE_NAME, timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, _hash_password(password)),
        )
        conn.commit()
        user_id_raw = cursor.lastrowid
        if user_id_raw is None:
            raise RuntimeError("Failed to retrieve user id")
        return int(user_id_raw)


def get_user_id(username: str, password: str | None = None) -> int | None:
    """Return user id for given username. If password is provided, verify it."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    if password is None:
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    else:
        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, _hash_password(password)),
        )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

if __name__ == '__main__':
    # このファイルを直接実行した場合、データベースを初期化する
    initialize_database()
