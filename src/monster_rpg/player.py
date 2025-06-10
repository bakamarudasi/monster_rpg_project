# player.py
import sqlite3
from .map_data import STARTING_LOCATION_ID
from .monsters.monster_class import Monster  # Monsterクラスをインポート
from .monsters.monster_data import ALL_MONSTERS  # モンスター定義をインポート
from .items.item_data import ALL_ITEMS
from .monsters.synthesis_rules import (
    SYNTHESIS_RECIPES,
    SYNTHESIS_ITEMS_REQUIRED,
    MONSTER_ITEM_RECIPES,
)
from .items.equipment import (
    ALL_EQUIPMENT,
    CRAFTING_RECIPES,
    create_titled_equipment,
    EquipmentInstance,
)
import random  # 将来的にスキル継承などで使うかも
import copy
from .monster_book import MonsterBook

# Debug flag to control verbose output
DEBUG_MODE = False

class Player:
    def __init__(self, name, player_level=1, gold=50, user_id=None):
        self.name = name
        self.player_level = player_level
        self.exp = 0
        self.party_monsters = []  # Monsterオブジェクトを格納
        # フォーメーション外の控えモンスターを保持するリスト
        self.reserve_monsters: list[Monster] = []
        self.gold = gold
        self.items = []
        self.equipment_inventory = []
        self.current_location_id = STARTING_LOCATION_ID
        self.db_id = None # データベース上のID (ロード時に設定)
        self.user_id = user_id
        self.exploration_progress = {}
        self.monster_book = MonsterBook()
        self.last_battle_log = []

    def save_game(self, db_name, user_id=None):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if user_id is not None:
            self.user_id = user_id
        if self.user_id is None:
            self.user_id = 1

        if self.db_id:
            cursor.execute(
                """
                UPDATE player_data
                SET name=?, player_level=?, exp=?, gold=?, current_location_id=?, user_id=?
                WHERE id=?
                """,
                (
                    self.name,
                    self.player_level,
                    self.exp,
                    self.gold,
                    self.current_location_id,
                    self.user_id,
                    self.db_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO player_data (user_id, name, player_level, exp, gold, current_location_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.user_id,
                    self.name,
                    self.player_level,
                    self.exp,
                    self.gold,
                    self.current_location_id,
                ),
            )
            self.db_id = cursor.lastrowid

        # パーティモンスターを保存
        cursor.execute("DELETE FROM party_monsters WHERE player_id=?", (self.db_id,))
        for monster in self.party_monsters:
            cursor.execute(
                "INSERT INTO party_monsters (player_id, monster_id, level, exp) VALUES (?, ?, ?, ?)",
                (self.db_id, monster.monster_id, monster.level, monster.exp),
            )

        # 控えモンスターを保存
        cursor.execute("DELETE FROM storage_monsters WHERE player_id=?", (self.db_id,))
        for monster in self.reserve_monsters:
            cursor.execute(
                "INSERT INTO storage_monsters (player_id, monster_id, level, exp) VALUES (?, ?, ?, ?)",
                (self.db_id, monster.monster_id, monster.level, monster.exp),
            )

        # 所持アイテムを保存
        cursor.execute("DELETE FROM player_items WHERE player_id=?", (self.db_id,))
        for item in self.items:
            item_id = getattr(item, "item_id", str(item))
            cursor.execute(
                "INSERT INTO player_items (player_id, item_id) VALUES (?, ?)",
                (self.db_id, item_id),
            )

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

    def get_exploration(self, location_id):
        return self.exploration_progress.get(location_id, 0)

    def increase_exploration(self, location_id, amount):
        current = self.exploration_progress.get(location_id, 0)
        new_value = min(100, current + amount)
        self.exploration_progress[location_id] = new_value
        return new_value

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
                new_monster_instance.mp = new_monster_instance.max_mp
                
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
            copied_monster.mp = copied_monster.max_mp
            print(f"{copied_monster.name} が仲間に加わった！")
            newly_added_monster = copied_monster
        else:
            print("エラー: add_monster_to_party の引数が不正です。")
        
        if newly_added_monster:
            print(f"[DEBUG player.py add_monster_to_party] Actual monster_id of added monster '{newly_added_monster.name}': '{newly_added_monster.monster_id}' (type: {type(newly_added_monster.monster_id)})")
            self.monster_book.record_captured(newly_added_monster.monster_id)


    def show_all_party_monsters_status(self):
        if not self.party_monsters:
            print(f"{self.name} はまだ仲間モンスターを持っていません。")
            return

        print(f"===== {self.name} のパーティーメンバー詳細 =====")
        for i, monster in enumerate(self.party_monsters):
            print(f"--- {i+1}. ---")
            monster.show_status()
        print("=" * 30)

    def move_monster(self, from_idx: int, to_idx: int) -> bool:
        """パーティ内でモンスターの位置を移動する。"""
        if not (
            0 <= from_idx < len(self.party_monsters)
            and 0 <= to_idx < len(self.party_monsters)
        ):
            return False
        monster = self.party_monsters.pop(from_idx)
        self.party_monsters.insert(to_idx, monster)
        return True

    def move_to_reserve(self, party_idx: int) -> bool:
        """指定したパーティメンバーを控えに移動する。"""
        if not (0 <= party_idx < len(self.party_monsters)):
            return False
        if len(self.party_monsters) <= 1:
            # 最低1体はパーティに残す
            return False
        monster = self.party_monsters.pop(party_idx)
        self.reserve_monsters.append(monster)
        return True

    def move_from_reserve(self, reserve_idx: int) -> bool:
        """控えからパーティにモンスターを移動する。"""
        if not (0 <= reserve_idx < len(self.reserve_monsters)):
            return False
        monster = self.reserve_monsters.pop(reserve_idx)
        self.party_monsters.append(monster)
        return True

    def reset_formation(self) -> None:
        """先頭のモンスターを残して他を控えに移す。"""
        while len(self.party_monsters) > 1:
            self.reserve_monsters.append(self.party_monsters.pop())

    def show_items(self):
        if not self.items:
            print("アイテムを何も持っていない。")
            return

        print("===== 所持アイテム =====")
        for i, item in enumerate(self.items, 1):
            name = getattr(item, "name", str(item))
            desc = getattr(item, "description", "")
            print(f"{i}. {name} - {desc}")
        print("=" * 20)

    def use_item(self, item_idx, target_monster):
        if not (0 <= item_idx < len(self.items)):
            print("無効なアイテム番号です。")
            return False

        item = self.items[item_idx]
        if not getattr(item, "usable", False):
            print(f"{item.name} はここでは使えない。")
            return False

        effect = getattr(item, "effect", {})
        if not effect:
            print("このアイテムはまだ効果が実装されていない。")
            return False

        etype = effect.get("type")

        if etype == "heal_hp":
            if target_monster is None:
                print("対象モンスターがいません。")
                return False
            if not target_monster.is_alive:
                print(f"{target_monster.name} は倒れているため回復できない。")
                return False
            amount = effect.get("amount", 0)
            before = target_monster.hp
            target_monster.hp = min(target_monster.max_hp, target_monster.hp + amount)
            healed = target_monster.hp - before
            print(f"{target_monster.name} のHPが {healed} 回復した。")
            self.items.pop(item_idx)
            return True

        if etype == "heal_mp":
            if target_monster is None:
                print("対象モンスターがいません。")
                return False
            amount = effect.get("amount", 0)
            before = target_monster.mp
            target_monster.mp = min(target_monster.max_mp, target_monster.mp + amount)
            restored = target_monster.mp - before
            print(f"{target_monster.name} のMPが {restored} 回復した。")
            self.items.pop(item_idx)
            return True

        if etype == "heal_full":
            if target_monster is None:
                print("対象モンスターがいません。")
                return False
            if not target_monster.is_alive:
                print(f"{target_monster.name} は倒れているため回復できない。")
                return False
            target_monster.hp = target_monster.max_hp
            target_monster.mp = target_monster.max_mp
            print(f"{target_monster.name} のHPとMPが全回復した！")
            self.items.pop(item_idx)
            return True

        if etype == "revive":
            if target_monster is None:
                print("対象モンスターがいません。")
                return False
            if target_monster.is_alive:
                print(f"{target_monster.name} はまだ倒れていない。")
                return False
            target_monster.is_alive = True
            amount = effect.get("amount", "half")
            if amount == "half":
                target_monster.hp = target_monster.max_hp // 2
            else:
                target_monster.hp = min(target_monster.max_hp, int(amount))
            print(f"{target_monster.name} が復活した！ HPが半分回復した。")
            self.items.pop(item_idx)
            return True

        print("このアイテムはまだ効果が実装されていない。")
        return False

    def rest_at_inn(self, cost):
        if self.gold >= cost:
            self.gold -= cost
            print(f"{cost}G を支払い、宿屋に泊まった。")
            for monster in self.party_monsters:
                monster.hp = monster.max_hp
                monster.mp = monster.max_mp
                monster.is_alive = True
            print("パーティは完全に回復した！")
            return True
        else:
            print("お金が足りない！宿屋に泊まれない...")
            return False

    def buy_item(self, item_id, price):
        if self.gold < price:
            print("お金が足りない！")
            return False
        if item_id not in ALL_ITEMS:
            print("そのアイテムは存在しない。")
            return False
        self.gold -= price
        self.items.append(ALL_ITEMS[item_id])
        print(f"{ALL_ITEMS[item_id].name} を {price}G で購入した。")
        return True

    def buy_monster(self, monster_id, price):
        if self.gold < price:
            print("お金が足りない！")
            return False
        if monster_id not in ALL_MONSTERS:
            print("そのモンスターは存在しない。")
            return False
        self.gold -= price
        self.add_monster_to_party(monster_id)
        print(f"{ALL_MONSTERS[monster_id].name} を {price}G で仲間にした。")
        return True

    def craft_equipment(self, equip_id):
        recipe = CRAFTING_RECIPES.get(equip_id)
        if not recipe:
            print("その装備は作成できない。")
            return None
        for item_id, qty in recipe.items():
            count = sum(1 for it in self.items if getattr(it, "item_id", None) == item_id)
            if count < qty:
                print("素材が足りない。")
                return None
        # consume items
        for item_id, qty in recipe.items():
            removed = 0
            for i in range(len(self.items)-1, -1, -1):
                if getattr(self.items[i], "item_id", None) == item_id and removed < qty:
                    self.items.pop(i)
                    removed += 1
        new_equip = create_titled_equipment(equip_id)
        if new_equip:
            self.equipment_inventory.append(new_equip)
            print(f"{new_equip.name} を作成した！")
            return new_equip
        print("装備の作成に失敗した。")
        return None

    def equip_to_monster(self, party_idx, equip_id):
        if not (0 <= party_idx < len(self.party_monsters)):
            print("無効なモンスター番号")
            return False
        equip = None
        for e in self.equipment_inventory:
            if isinstance(e, EquipmentInstance):
                if e.instance_id == equip_id or e.base_item.equip_id == equip_id:
                    equip = e
                    break
            else:
                if getattr(e, "equip_id", None) == equip_id:
                    equip = e
                    break
        if not equip:
            print("その装備を所持していない。")
            return False
        monster = self.party_monsters[party_idx]
        monster.equip(equip)
        self.equipment_inventory.remove(equip)
        print(f"{monster.name} に {equip.name} を装備した。")
        return True

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

        if DEBUG_MODE:
            print("[DEBUG player.py] Synthesizing with:")
            print(f"[DEBUG player.py]   Parent 1: name='{parent1.name}', monster_id='{parent1.monster_id}' (type: {type(parent1.monster_id)})")
            print(f"[DEBUG player.py]   Parent 2: name='{parent2.name}', monster_id='{parent2.monster_id}' (type: {type(parent2.monster_id)})")

        if not parent1.monster_id or not parent2.monster_id:
            return False, "エラー: 合成元のモンスターにIDが設定されていません。", None
            
        id1_lower = parent1.monster_id.lower() # ここで日本語の monster_id が小文字化される（日本語のまま）
        id2_lower = parent2.monster_id.lower() # 同上
        
        recipe_key_parts = sorted([id1_lower, id2_lower])
        recipe_key = tuple(recipe_key_parts)
        
        if DEBUG_MODE:
            print(f"[DEBUG player.py]   ID1 original: '{parent1.monster_id}', ID1 lower: '{id1_lower}'")
            print(f"[DEBUG player.py]   ID2 original: '{parent2.monster_id}', ID2 lower: '{id2_lower}'")
            print(f"[DEBUG player.py]   Recipe key parts (sorted): {recipe_key_parts}")
            print(f"[DEBUG player.py]   Recipe key for lookup: {recipe_key}")
            print(f"[DEBUG player.py]   Available recipes in SYNTHESIS_RECIPES: {SYNTHESIS_RECIPES}")

        if recipe_key in SYNTHESIS_RECIPES:
            # 合成に必要なアイテムがあればチェック
            required_item = SYNTHESIS_ITEMS_REQUIRED.get(recipe_key)
            if required_item:
                item_index = next(
                    (i for i, itm in enumerate(self.items) if getattr(itm, "item_id", None) == required_item),
                    None,
                )
                if item_index is None:
                    item_name = ALL_ITEMS[required_item].name if required_item in ALL_ITEMS else required_item
                    return False, f"合成には {item_name} が必要だ。", None
                # 消費アイテムとして取り除く
                self.items.pop(item_index)

            result_monster_id = SYNTHESIS_RECIPES[recipe_key]

            if result_monster_id in ALL_MONSTERS:
                base_new_monster_template = ALL_MONSTERS[result_monster_id]
                new_monster = base_new_monster_template.copy()
                if new_monster is None:  # copy()が失敗した場合
                    return False, f"エラー: 合成結果のモンスター '{result_monster_id}' の生成に失敗しました。", None

                # --------------------------------------------------
                # ▼ 継承システム: スキルとステータスボーナス
                # --------------------------------------------------
                inherited_skills = []
                for parent in (parent1, parent2):
                    if parent.skills:
                        skill = random.choice(parent.skills)
                        current_names = [s.name for s in new_monster.skills + inherited_skills]
                        if getattr(skill, "name", None) not in current_names:
                            inherited_skills.append(copy.deepcopy(skill))

                new_monster.skills.extend(inherited_skills)

                avg_level = (parent1.level + parent2.level) / 2
                hp_bonus = int(avg_level * 2)
                atk_bonus = int(avg_level)
                def_bonus = int(avg_level)
                spd_bonus = int(avg_level * 0.5)

                new_monster.max_hp += hp_bonus
                new_monster.attack += atk_bonus
                new_monster.defense += def_bonus
                new_monster.speed += spd_bonus

                # 初期状態を整える
                new_monster.level = 1
                new_monster.exp = 0
                new_monster.hp = new_monster.max_hp
                new_monster.is_alive = True

                indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
                removed_monster_names = []
                for idx in indices_to_remove:
                    removed_monster_names.append(self.party_monsters.pop(idx).name)

                self.party_monsters.append(new_monster)

                return (
                    True,
                    f"{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {new_monster.name} が誕生した！",
                    new_monster,
                )
            else:
                return False, f"エラー: 合成結果のモンスターID '{result_monster_id}' がモンスター定義に存在しません。", None
        else:
            return False, f"{parent1.name} と {parent2.name} の組み合わせでは何も生まれなかった...", None


    def synthesize_monster_with_item(self, monster_idx, item_id):
        """Combine a single monster and an item to create a new monster."""
        if not (0 <= monster_idx < len(self.party_monsters)):
            return False, "無効なモンスターの選択です。", None

        item_index = next(
            (i for i, it in enumerate(self.items) if getattr(it, "item_id", None) == item_id),
            None,
        )
        if item_index is None:
            return False, "そのアイテムを所持していない。", None

        parent = self.party_monsters[monster_idx]
        recipe_key = (parent.monster_id.lower(), item_id)

        if recipe_key not in MONSTER_ITEM_RECIPES:
            item_name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
            return False, f"{parent.name} と {item_name} では何も起こらなかった...", None

        result_id = MONSTER_ITEM_RECIPES[recipe_key]
        if result_id not in ALL_MONSTERS:
            return False, f"エラー: 合成結果のモンスターID '{result_id}' が見つかりません。", None

        new_mon = ALL_MONSTERS[result_id].copy()
        if new_mon is None:
            return False, f"エラー: 合成結果のモンスター '{result_id}' の生成に失敗しました。", None

        # consume materials
        removed_name = self.party_monsters.pop(monster_idx).name
        self.items.pop(item_index)

        new_mon.level = 1
        new_mon.exp = 0
        new_mon.hp = new_mon.max_hp
        new_mon.is_alive = True
        self.party_monsters.append(new_mon)

        item_name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
        return True, f"{removed_name} と {item_name} を合成して {new_mon.name} が誕生した！", new_mon


    @staticmethod
    def load_game(db_name, user_id=1):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, player_level, exp, gold, current_location_id, user_id FROM player_data WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()

        if row:
            db_id, name, level, exp, gold, location_id, u_id = row
            loaded_player = Player(name, player_level=level, gold=gold, user_id=u_id)
            loaded_player.exp = exp
            loaded_player.current_location_id = location_id
            loaded_player.db_id = db_id

            # パーティモンスターを読み込む
            cursor.execute(
                "SELECT monster_id, level, exp FROM party_monsters WHERE player_id=?",
                (db_id,),
            )
            for monster_id, m_level, m_exp in cursor.fetchall():
                if monster_id in ALL_MONSTERS:
                    monster = ALL_MONSTERS[monster_id].copy()
                    while monster.level < m_level:
                        monster.gain_exp(monster.calculate_exp_to_next_level())
                    monster.exp = m_exp
                    loaded_player.party_monsters.append(monster)

            # 控えモンスターを読み込む
            cursor.execute(
                "SELECT monster_id, level, exp FROM storage_monsters WHERE player_id=?",
                (db_id,),
            )
            for monster_id, m_level, m_exp in cursor.fetchall():
                if monster_id in ALL_MONSTERS:
                    monster = ALL_MONSTERS[monster_id].copy()
                    while monster.level < m_level:
                        monster.gain_exp(monster.calculate_exp_to_next_level())
                    monster.exp = m_exp
                    loaded_player.reserve_monsters.append(monster)

            # 所持アイテムを読み込む
            cursor.execute(
                "SELECT item_id FROM player_items WHERE player_id=?",
                (db_id,),
            )
            for (item_id,) in cursor.fetchall():
                if item_id in ALL_ITEMS:
                    loaded_player.items.append(ALL_ITEMS[item_id])

            conn.close()
            print(f"{name} のデータがロードされました。")
            return loaded_player
        else:
            conn.close()
            print("セーブデータが見つかりませんでした。")
            return None
