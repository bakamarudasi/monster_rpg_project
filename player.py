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
        if isinstance(monster_id_or_object, str): # モンスターIDの場合
            monster_id = monster_id_or_object
            if monster_id in ALL_MONSTERS:
                # ALL_MONSTERSのテンプレートから新しいインスタンスをコピーして仲間にする
                new_monster_instance = ALL_MONSTERS[monster_id].copy()
                # 仲間にする際は通常レベル1、経験値0、HP最大で初期化することが多い
                new_monster_instance.level = 1 # またはALL_MONSTERS[monster_id].level
                new_monster_instance.exp = 0
                new_monster_instance.max_hp = ALL_MONSTERS[monster_id].max_hp # 初期max_hp
                new_monster_instance.hp = new_monster_instance.max_hp
                new_monster_instance.attack = ALL_MONSTERS[monster_id].attack # 初期attack
                new_monster_instance.defense = ALL_MONSTERS[monster_id].defense # 初期defense
                # スキルも初期状態に戻すか、コピー元のスキルを引き継ぐか設計による
                # new_monster_instance.skills = [s.copy() for s in ALL_MONSTERS[monster_id].skills]


                self.party_monsters.append(new_monster_instance)
                print(f"{new_monster_instance.name} が仲間に加わった！")
            else:
                print(f"エラー: モンスターID '{monster_id}' は存在しません。")
        elif isinstance(monster_id_or_object, Monster): # Monsterオブジェクトの場合
            monster_object = monster_id_or_object
            # オブジェクトを直接追加する場合、それがコピーであることを確認するか、
            # 意図的に同じインスタンスを共有するかを考慮する。
            # 通常はコピーを追加するのが安全。
            self.party_monsters.append(monster_object.copy()) # ここでもコピーが望ましい
            print(f"{monster_object.name} が仲間に加わった！")
        else:
            print("エラー: add_monster_to_party の引数が不正です。")


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

        # レシピ検索のためにモンスターIDをソートしてタプル化
        # (parent1.monster_id と parent2.monster_id が設定されている前提)
        if not parent1.monster_id or not parent2.monster_id:
            return False, "エラー: 合成元のモンスターにIDが設定されていません。", None
            
        recipe_key_parts = sorted([parent1.monster_id.lower(), parent2.monster_id.lower()])
        recipe_key = tuple(recipe_key_parts)

        if recipe_key in SYNTHESIS_RECIPES:
            result_monster_id = SYNTHESIS_RECIPES[recipe_key]
            
            if result_monster_id in ALL_MONSTERS:
                # 新しいモンスターをALL_MONSTERSのテンプレートからコピーして生成
                base_new_monster = ALL_MONSTERS[result_monster_id]
                new_monster = base_new_monster.copy() # Monsterクラスのcopyメソッドを使用

                # 合成後のモンスターの初期化 (例: レベル1、HP最大)
                new_monster.level = 1
                new_monster.exp = 0
                # ステータスはALL_MONSTERSの定義時点のものをコピーしているので、
                # レベル1の基本ステータスになっているはず。
                # max_hpとhpも再設定
                new_monster.max_hp = ALL_MONSTERS[result_monster_id].max_hp # 初期max_hp
                new_monster.hp = new_monster.max_hp
                new_monster.attack = ALL_MONSTERS[result_monster_id].attack # 初期attack
                new_monster.defense = ALL_MONSTERS[result_monster_id].defense # 初期defense
                new_monster.is_alive = True
                
                # TODO: スキル継承ロジック (オプション)
                # 例: 親のスキルをいくつか引き継ぐなど
                # new_monster.skills = [] # いったん空にするか、基本スキルを設定
                # inherited_skills = set()
                # for skill in parent1.skills:
                #     if len(inherited_skills) < 2: # 例: 親1から2つまで
                #         inherited_skills.add(skill)
                # for skill in parent2.skills:
                #     if len(inherited_skills) < 4: # 例: 親2からさらに追加して合計4つまで
                #         inherited_skills.add(skill)
                # new_monster.skills = list(inherited_skills)


                # 親モンスターをパーティから削除
                # インデックスが大きい方から削除しないと、小さい方を先に消すとインデックスがずれる
                indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
                removed_monster_names = []
                for idx in indices_to_remove:
                    removed_monster_names.append(self.party_monsters.pop(idx).name)
                
                # 新しいモンスターをパーティに追加
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
            
            # TODO: パーティモンスターやアイテムのロード処理もここに追加する (ステップ1の課題)
            # 例:
            # loaded_player.party_monsters = load_party_monsters_from_db(db_id)
            # loaded_player.items = load_items_from_db(db_id)
            
            print(f"{name} のデータがロードされました。")
            return loaded_player
        else:
            print("セーブデータが見つかりませんでした。")
            return None

