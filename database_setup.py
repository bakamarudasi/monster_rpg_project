# database_setup.py (新規作成)
import sqlite3

DATABASE_NAME = "monster_rpg_save.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # player_data テーブルの作成 (存在しなければ)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL,
        player_level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        gold INTEGER DEFAULT 0,
        current_location_id TEXT
    )
    """)
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

    conn.commit()
    conn.close()
    print("データベースの初期化が完了しました (または既に初期化済みです)。")

if __name__ == '__main__':
    # このファイルを直接実行した場合、データベースを初期化する
    initialize_database()
