# player.py (新規ファイル)
import sqlite3
# from monsters.definitions import Monster # 将来的には型ヒントなどで使うかもしれませんが、まずは無くてもOK
from map_data import STARTING_LOCATION_ID
class Player:
    def __init__(self, name, player_level=1, gold=50): # 初期レベルと初期ゴールドを設定
        self.name = name
        self.player_level = player_level
        self.exp = 0  # 主人公自身の経験値
        self.party_monsters = []  # 手持ちモンスターのリスト (Monsterオブジェクトを格納)
        self.gold = gold
        self.items = []  # 所持アイテムのリスト (最初は空)
        self.current_location_id = STARTING_LOCATION_ID  # 初期位置を設定 (map_data.py からインポート)
        self.db_initialized = False  # データベース初期化フラグ
        
    def save_game(self, db_name): # データベースファイル名を引数で受け取る
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if self.db_id: # 既に保存されたことがあり、IDを持っている場合 (更新)
            cursor.execute("""
            UPDATE player_data 
            SET name=?, player_level=?, exp=?, gold=?, current_location_id=?
            WHERE id=?
            """, (self.name, self.player_level, self.exp, self.gold, self.current_location_id, self.db_id))
        else: # 初めて保存する場合 (新規作成)
            cursor.execute("""
            INSERT INTO player_data (name, player_level, exp, gold, current_location_id)
            VALUES (?, ?, ?, ?, ?)
            """, (self.name, self.player_level, self.exp, self.gold, self.current_location_id))
            self.db_id = cursor.lastrowid # 新しく割り振られたIDを保存

        conn.commit()
        conn.close()
        print(f"{self.name} のデータがセーブされました。")

    def show_status(self):
        """主人公の現在のステータスを表示します。"""
        print(f"===== {self.name} のステータス =====")
        print(f"レベル: {self.player_level}")
        print(f"経験値: {self.exp}")
        print(f"所持金: {self.gold} G")
        print(f"手持ちモンスター: {len(self.party_monsters)}体")
        if self.party_monsters:
            print("--- パーティーメンバー ---")
            for i, monster in enumerate(self.party_monsters):
                # Monsterオブジェクトに name と level 属性がある前提
                print(f"  {i+1}. {monster.name} (Lv.{monster.level})")
            print("------------------------")
        else:
            print("  (まだ仲間モンスターがいません)")
        # アイテム表示は後で充実させましょう
        # if self.items:
        # print(f"所持アイテム: {', '.join(self.items)}")
        # else:
        # print(" (アイテムを持っていません)")
        print("=" * 26)

    def add_monster_to_party(self, monster):
        """手持ちモンスターに新しいモンスターを加えます。"""
        # 現状は単純に追加。将来的にはパーティ上限数や重複チェックなどを強化できます。
        if monster not in self.party_monsters:
            self.party_monsters.append(monster)
            print(f"{monster.name} が仲間に加わった！")
        else:
            print(f"{monster.name} は既にパーティーにいます。")

    def show_all_party_monsters_status(self):
        """手持ちモンスター全員の詳細ステータスを表示します。"""
        if not self.party_monsters:
            print(f"{self.name} はまだ仲間モンスターを持っていません。")
            return

        print(f"===== {self.name} のパーティーメンバー詳細 =====")
        for monster in self.party_monsters:
            monster.show_status() # 各Monsterインスタンスのshow_status()を呼び出す
        print("=" * 30)

    # --- 将来追加するかもしれないメソッド ---
    # def gain_exp(self, amount):
    #     """主人公が経験値を獲得します。"""
    #     self.exp += amount
    #     print(f"{self.name}は {amount} の経験値を獲得した！")
    #     # レベルアップ処理などもここに追加
    #
    # def add_item(self, item_name):
    #     """アイテムを入手します。"""
    #     self.items.append(item_name)
    #     print(f"{item_name} を手に入れた！")
    # player.py の Player クラスに追加
    def rest_at_inn(self, cost):
        if self.gold >= cost:
            self.gold -= cost
            print(f"{cost}G を支払い、宿屋に泊まった。")
            for monster in self.party_monsters:
                monster.hp = monster.max_hp
                monster.is_alive = True
                # 将来的には状態異常などもここで回復
                # monster.status_effects = []
            print("パーティは完全に回復した！")
            return True
        else:
            print("お金が足りない！宿屋に泊まれない...")
            return False
        
    # player.py の Player クラスに追加 (またはクラスメソッドや外部関数として)
@staticmethod # Playerインスタンスを作る前に呼ぶので静的メソッドが良いかも
def load_game(db_name): # データベースファイル名
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # ID=1 のプレイヤーデータをロードする想定 (または最後にセーブされたデータなど)
    cursor.execute("SELECT id, name, player_level, exp, gold, current_location_id FROM player_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        db_id, name, level, exp, gold, location_id = row
        loaded_player = Player(name, player_level=level, gold=gold) # Playerインスタンス再作成
        loaded_player.exp = exp
        loaded_player.current_location_id = location_id
        loaded_player.db_id = db_id # ロードしたデータのIDを保持
        print(f"{name} のデータがロードされました。")
        return loaded_player
    else:
        print("セーブデータが見つかりませんでした。")
        return None