# player.py
import sqlite3
from map_data import STARTING_LOCATION_ID
from monsters.monster_class import Monster # Monsterクラスをインポート
from monsters.monster_data import ALL_MONSTERS # モンスター定義をインポート
from synthesis_rules import SYNTHESIS_RECIPES # 合成レシピをインポート
import random # 将来的にスキル継承などで使うかも

class Player:
    def __init__(self, name, player_level=1, gold=50):
        self.name = name
        self.player_level = player_level
        self.exp = 0
        self.party_monsters = [] # Monsterオブジェクトを格納
        self.gold = gold
        self.items = []
        self.current_location_id = STARTING_LOCATION_ID
        self.db_id = None # データベース上のID (ロード時に設定)

    def save_game(self, db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if self.db_id:
            cursor.execute("""
            UPDATE player_data 
            SET name=?, player_level=?, exp=?, gold=?, current_location_id=?
            WHERE id=?
            """, (self.name, self.player_level, self.exp, self.gold, self.current_location_id, self.db_id))
        else:
            cursor.execute("""
            INSERT INTO player_data (name, player_level, exp, gold, current_location_id)
            VALUES (?, ?, ?, ?, ?)
            """, (self.name, self.player_level, self.exp, self.gold, self.current_location_id))
            self.db_id = cursor.lastrowid

        # TODO: パーティモンスターやアイテムの保存処理もここに追加する (ステップ1の課題)

        conn.commit()
        conn.close()
        print(f"{self.name} のデータがセーブされました。")

    def show_status(self):
        print(f"===== {self.name} のステータス =====")
        print(f"レベル: {self.player_level}")
        print(f"経験値: {self.exp}")
        print(f"所持金: {self.gold} G")
        print(f"手持ちモンスター: {len(self.party_monsters)}体")
        if self.party_monsters:
            print("--- パーティーメンバー ---")
            for i, monster in enumerate(self.party_monsters):
                print(f"  {i+1}. {monster.name} (ID: {monster.monster_id}, Lv.{monster.level})") # IDも表示
            print("------------------------")
        else:
            print("  (まだ仲間モンスターがいません)")
        print("=" * 26)

    def add_monster_to_party(self, monster_id_or_object):
        """
        手持ちモンスターに新しいモンスターを加えます。
        引数はモンスターID (ALL_MONSTERSのキー) または Monsterオブジェクト。
        """
        newly_added_monster = None # 追加されたモンスターを一時的に保持
        if isinstance(monster_id_or_object, str): # モンスターIDの場合
            monster_id_key = monster_id_or_object.lower() # 確実に小文字で検索
            if monster_id_key in ALL_MONSTERS:
                # ALL_MONSTERSのテンプレートから新しいインスタンスをコピーして仲間にする
                # print(f"[DEBUG player.py add_monster_to_party] Copying from ALL_MONSTERS with key: '{monster_id_key}'")
                # print(f"[DEBUG player.py add_monster_to_party]   Template monster_id: '{ALL_MONSTERS[monster_id_key].monster_id}'")
                new_monster_instance = ALL_MONSTERS[monster_id_key].copy()
                if new_monster_instance is None: # copy()が失敗した場合
                    print(f"エラー: モンスター '{monster_id_key}' のコピーに失敗しました。")
                    return

                # 仲間にする際は通常レベル1、経験値0、HP最大で初期化することが多い
                new_monster_instance.level = 1 # またはALL_MONSTERS[monster_id_key].level
                new_monster_instance.exp = 0
                new_monster_instance.hp = new_monster_instance.max_hp # HPは最大に
                
                self.party_monsters.append(new_monster_instance)
                print(f"{new_monster_instance.name} が仲間に加わった！")
                newly_added_monster = new_monster_instance
            else:
                print(f"エラー: モンスターID '{monster_id_key}' は存在しません。")
        elif isinstance(monster_id_or_object, Monster): # Monsterオブジェクトの場合
            monster_object = monster_id_or_object
            # print(f"[DEBUG player.py add_monster_to_party] Copying from Monster object: name='{monster_object.name}', monster_id='{monster_object.monster_id}'")
            copied_monster = monster_object.copy()
            if copied_monster is None: # copy()が失敗した場合
                print(f"エラー: モンスターオブジェクト '{monster_object.name}' のコピーに失敗しました。")
                return

            self.party_monsters.append(copied_monster) 
            print(f"{copied_monster.name} が仲間に加わった！")
            newly_added_monster = copied_monster
        else:
            print("エラー: add_monster_to_party の引数が不正です。")
        
        if newly_added_monster:
            print(f"[DEBUG player.py add_monster_to_party] Actual monster_id of added monster '{newly_added_monster.name}': '{newly_added_monster.monster_id}' (type: {type(newly_added_monster.monster_id)})")


    def show_all_party_monsters_status(self):
        if not self.party_monsters:
            print(f"{self.name} はまだ仲間モンスターを持っていません。")
            return

        print(f"===== {self.name} のパーティーメンバー詳細 =====")
        for i, monster in enumerate(self.party_monsters):
            print(f"--- {i+1}. ---")
            monster.show_status()
        print("=" * 30)

    def rest_at_inn(self, cost):
        if self.gold >= cost:
            self.gold -= cost
            print(f"{cost}G を支払い、宿屋に泊まった。")
            for monster in self.party_monsters:
                monster.hp = monster.max_hp
                monster.is_alive = True
            print("パーティは完全に回復した！")
            return True
        else:
            print("お金が足りない！宿屋に泊まれない...")
            return False

    def synthesize_monster(self, monster1_idx, monster2_idx, item_id=None): # item_id は将来用
        """
        指定された2体のモンスターを合成して新しいモンスターを生成します。
        合成に使用したモンスターはパーティからいなくなります。
        :param monster1_idx: パーティ内の1体目のモンスターのインデックス
        :param monster2_idx: パーティ内の2体目のモンスターのインデックス
        :param item_id: (オプション) 合成に必要なアイテムのID
        :return: (成功フラグ, メッセージ, 新しいモンスターオブジェクト or None)
        """
        if not (0 <= monster1_idx < len(self.party_monsters) and \
                0 <= monster2_idx < len(self.party_monsters)):
            return False, "無効なモンスターの選択です。", None
        
        if monster1_idx == monster2_idx:
            return False, "同じモンスター同士は合成できません。", None

        parent1 = self.party_monsters[monster1_idx]
        parent2 = self.party_monsters[monster2_idx]

        # --- デバッグプリント追加 ---
        print(f"[DEBUG player.py] Synthesizing with:")
        print(f"[DEBUG player.py]   Parent 1: name='{parent1.name}', monster_id='{parent1.monster_id}' (type: {type(parent1.monster_id)})")
        print(f"[DEBUG player.py]   Parent 2: name='{parent2.name}', monster_id='{parent2.monster_id}' (type: {type(parent2.monster_id)})")
        # --- デバッグプリント追加ここまで ---

        if not parent1.monster_id or not parent2.monster_id:
            return False, "エラー: 合成元のモンスターにIDが設定されていません。", None
            
        id1_lower = parent1.monster_id.lower() # ここで日本語の monster_id が小文字化される（日本語のまま）
        id2_lower = parent2.monster_id.lower() # 同上
        
        recipe_key_parts = sorted([id1_lower, id2_lower])
        recipe_key = tuple(recipe_key_parts)
        
        # --- デバッグプリント追加 ---
        print(f"[DEBUG player.py]   ID1 original: '{parent1.monster_id}', ID1 lower: '{id1_lower}'")
        print(f"[DEBUG player.py]   ID2 original: '{parent2.monster_id}', ID2 lower: '{id2_lower}'")
        print(f"[DEBUG player.py]   Recipe key parts (sorted): {recipe_key_parts}")
        print(f"[DEBUG player.py]   Recipe key for lookup: {recipe_key}")
        print(f"[DEBUG player.py]   Available recipes in SYNTHESIS_RECIPES: {SYNTHESIS_RECIPES}")
        # --- デバッグプリント追加ここまで ---

        if recipe_key in SYNTHESIS_RECIPES:
            result_monster_id = SYNTHESIS_RECIPES[recipe_key]
            
            if result_monster_id in ALL_MONSTERS:
                base_new_monster_template = ALL_MONSTERS[result_monster_id]
                # print(f"[DEBUG player.py synthesize_monster] Template for new monster '{result_monster_id}': monster_id='{base_new_monster_template.monster_id}'")
                new_monster = base_new_monster_template.copy()
                if new_monster is None: # copy()が失敗した場合
                    return False, f"エラー: 合成結果のモンスター '{result_monster_id}' の生成に失敗しました。", None

                new_monster.level = 1
                new_monster.exp = 0
                new_monster.hp = new_monster.max_hp # HPは最大に
                new_monster.is_alive = True
                # print(f"[DEBUG player.py synthesize_monster] Newly synthesized monster: name='{new_monster.name}', monster_id='{new_monster.monster_id}'")
                
                indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
                removed_monster_names = []
                for idx in indices_to_remove:
                    removed_monster_names.append(self.party_monsters.pop(idx).name)
                
                self.party_monsters.append(new_monster)
                
                return True, f"{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {new_monster.name} が誕生した！", new_monster
            else:
                return False, f"エラー: 合成結果のモンスターID '{result_monster_id}' がモンスター定義に存在しません。", None
        else:
            return False, f"{parent1.name} と {parent2.name} の組み合わせでは何も生まれなかった...", None


    @staticmethod
    def load_game(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, player_level, exp, gold, current_location_id FROM player_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            db_id, name, level, exp, gold, location_id = row
            loaded_player = Player(name, player_level=level, gold=gold)
            loaded_player.exp = exp
            loaded_player.current_location_id = location_id
            loaded_player.db_id = db_id
            
            print(f"{name} のデータがロードされました。")
            return loaded_player
        else:
            print("セーブデータが見つかりませんでした。")
            return None
