from ..skills.skills import ALL_SKILLS
import copy  # deepcopyのためにインポート
from .evolution_rules import EVOLUTION_RULES

GROWTH_TYPE_AVERAGE = "平均型"
GROWTH_TYPE_EARLY = "早熟型"
GROWTH_TYPE_LATE = "大器晩成型"

# モンスターランク定義 (monster_data.pyと共通で使う場合は、別の共通ファイルに定義するのも良い)
RANK_S = "S"
RANK_A = "A"
RANK_B = "B"
RANK_C = "C"
RANK_D = "D"

def get_status_gains_average(current_level):
    hp_gain = 5 + (current_level // 5)
    attack_gain = 2 + (current_level // 10)
    defense_gain = 2 + (current_level // 10)
    speed_gain = attack_gain
    return {
        "hp": hp_gain,
        "attack": attack_gain,
        "defense": defense_gain,
        "speed": speed_gain,
    }

def get_status_gains_early(current_level):
    if current_level <= 10:
        hp_gain = 8 + (current_level // 3)
        attack_gain = 3 + (current_level // 5)
        defense_gain = 3 + (current_level // 5)
    elif current_level <= 25:
        hp_gain = 4 + (current_level // 6)
        attack_gain = 1 + (current_level // 8)
        defense_gain = 1 + (current_level // 8)
    else:
        hp_gain = 3
        attack_gain = 1
        defense_gain = 1
    speed_gain = attack_gain
    return {
        "hp": hp_gain,
        "attack": attack_gain,
        "defense": defense_gain,
        "speed": speed_gain,
    }

def get_status_gains_late(current_level):
    if current_level <= 15:
        hp_gain = 3 + (current_level // 7)
        attack_gain = 1 + (current_level // 10)
        defense_gain = 1 + (current_level // 10)
    elif current_level <= 30:
        hp_gain = 6 + (current_level // 5)
        attack_gain = 2 + (current_level // 8)
        defense_gain = 2 + (current_level // 8)
    else:
        hp_gain = 10 + (current_level // 4)
        attack_gain = 4 + (current_level // 6)
        defense_gain = 4 + (current_level // 6)
    speed_gain = attack_gain
    return {
        "hp": hp_gain,
        "attack": attack_gain,
        "defense": defense_gain,
        "speed": speed_gain,
    }

def calculate_exp_for_average(current_level):
    return (current_level ** 2) * 20 + 50

def calculate_exp_for_early(current_level):
    if current_level < 10:
        return (current_level ** 2) * 15 + 30
    elif current_level < 30:
        return (current_level ** 2) * 25 + 100
    else:
        return (current_level ** 3) * 10 + 500

def calculate_exp_for_late(current_level):
    if current_level < 15:
        return (current_level ** 2) * 30 + 100
    else:
        return (current_level ** 2) * 20 + 50

class Monster:
    def __init__(self, name, hp, attack, defense, mp=30, level=1, exp=0, element=None, skills=None,
                 growth_type=GROWTH_TYPE_AVERAGE, monster_id=None, image_filename=None,
                 rank=RANK_D, speed=5, drop_items=None, scout_rate=0.25, learnset=None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.attack = attack
        self.defense = defense
        self.level = level
        self.exp = exp
        self.element = element
        self.skills = skills if skills else []
        self.status_effects = []
        self.is_alive = True
        self.growth_type = growth_type
        
        if monster_id is not None and isinstance(monster_id, str) and monster_id.strip() != "":
            self.monster_id = monster_id
        else:
            self.monster_id = name.lower()
        
        self.image_filename = image_filename
        self.rank = rank 
        self.speed = speed  # speed 属性を保存
        self.drop_items = drop_items if drop_items else []
        self.scout_rate = scout_rate  # スカウト成功率(0.0-1.0)
        # 装備品スロット (weapon, armor など)
        self.equipment = {}
        self.learnset = learnset if learnset else {}

    def show_status(self):
        print(f"名前: {self.name} (ID: {self.monster_id}, Lv.{self.level}, Rank: {self.rank})") 
        if self.element:
            print(f"属性: {self.element}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"MP: {self.mp}/{self.max_mp}")
        print(f"攻撃力: {self.attack}")
        print(f"防御力: {self.defense}")
        print(f"素早さ: {self.speed}") # 素早さを表示
        exp_needed = self.calculate_exp_to_next_level()
        print(f"経験値: {self.exp}/{exp_needed if exp_needed is not None else 'N/A'}")
        if self.skills:
            print("スキル:")
            for skill_obj in self.skills:
                if hasattr(skill_obj, 'describe') and callable(skill_obj.describe):
                    print(f"  - {skill_obj.describe()}")
                else:
                    print(f"  - {skill_obj.name}")
        else:
            print("  (スキルなし)")
        if self.status_effects:
            effect_names = ", ".join(effect['name'] for effect in self.status_effects)
            print(f"状態異常: {effect_names}")
        print("-" * 20)

    def equip(self, equipment):
        """Equip an Equipment object to this monster."""
        if equipment is None:
            return
        self.equipment[equipment.slot] = equipment

    def total_attack(self):
        bonus = sum(getattr(e, 'attack', 0) for e in self.equipment.values())
        return self.attack + bonus

    def total_defense(self):
        bonus = sum(getattr(e, 'defense', 0) for e in self.equipment.values())
        return self.defense + bonus

    def _try_evolution(self):
        """Check evolution rules and evolve if conditions are met."""
        rule = EVOLUTION_RULES.get(self.monster_id)
        if not rule:
            return
        if self.level < rule.get('level', 0):
            return
        req_skill = rule.get('requires_skill')
        if req_skill:
            if not any(getattr(s, 'name', '') == req_skill for s in self.skills):
                return
        from .monster_data import ALL_MONSTERS  # local import to avoid cycle
        new_id = rule.get('evolves_to')
        template = ALL_MONSTERS.get(new_id)
        if not template:
            return
        evolved = template.copy()
        evolved.level = self.level
        evolved.exp = self.exp
        evolved.equipment = getattr(self, 'equipment', {}).copy()
        self.__dict__.update(evolved.__dict__)
        print(f"{template.name} に進化した！")

    def _learn_skills_for_level(self):
        if not isinstance(getattr(self, "learnset", None), dict):
            return
        skill_ids = self.learnset.get(self.level)
        if not skill_ids:
            return
        if isinstance(skill_ids, str):
            skill_ids = [skill_ids]
        for sid in skill_ids:
            template = ALL_SKILLS.get(sid)
            if template is None:
                continue
            if any(getattr(s, "name", None) == template.name for s in self.skills):
                continue
            self.skills.append(copy.deepcopy(template))
            print(f"{self.name} は {template.name} を覚えた！")

    def calculate_exp_to_next_level(self):
        if self.growth_type == GROWTH_TYPE_EARLY:
            exp_needed = calculate_exp_for_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            exp_needed = calculate_exp_for_late(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            exp_needed = calculate_exp_for_average(self.level)
        else:
            print(f"警告: 未知の成長タイプ '{self.growth_type}' が指定されました。平均型として計算します。")
            exp_needed = calculate_exp_for_average(self.level)
        return exp_needed

    def gain_exp(self, amount):
        if not self.is_alive:
            return

        self.exp += amount
        print(f"{self.name} は {amount} の経験値を獲得した！ (現在EXP: {self.exp})")

        exp_needed_for_next_level = self.calculate_exp_to_next_level()
        if exp_needed_for_next_level is None:
            return

        while self.exp >= exp_needed_for_next_level and self.is_alive:
            self.exp -= exp_needed_for_next_level
            self.level_up()

            exp_needed_for_next_level = self.calculate_exp_to_next_level()
            if exp_needed_for_next_level is None:
                break

        if self.exp < 0:
            self.exp = 0

    def level_up(self):
        self.level += 1
        print(f"🎉🎉🎉 {self.name} は レベル {self.level} に上がった！ 🎉🎉�")

        status_gains_dict = {}
        if self.growth_type == GROWTH_TYPE_EARLY:
            status_gains_dict = get_status_gains_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            status_gains_dict = get_status_gains_late(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            status_gains_dict = get_status_gains_average(self.level)
        else:
            print(f"警告: 未知の成長タイプ '{self.growth_type}'。平均型のステータス上昇を適用します。")
            status_gains_dict = get_status_gains_average(self.level)
        
        if not isinstance(status_gains_dict, dict):
            status_gains_dict = {}

        status_gains_dict.setdefault("hp", 0)
        status_gains_dict.setdefault("attack", 0)
        status_gains_dict.setdefault("defense", 0)
        status_gains_dict.setdefault("speed", 0)

        hp_increase = status_gains_dict["hp"]
        attack_increase = status_gains_dict["attack"]
        defense_increase = status_gains_dict["defense"]
        speed_increase = status_gains_dict["speed"]
            
        self.max_hp += hp_increase
        self.hp = self.max_hp 
        self.attack += attack_increase
        self.defense += defense_increase
        self.speed += speed_increase

        print(
            f"最大HPが {hp_increase}、攻撃力が {attack_increase}、防御力が {defense_increase}、素早さが {speed_increase} 上昇した！"
        )

        self._try_evolution()
        self._learn_skills_for_level()

    def copy(self):
        new_skills = [copy.deepcopy(skill) for skill in self.skills]
        
        new_monster = Monster(
            name=self.name,
            hp=self.max_hp, 
            attack=self.attack,
            defense=self.defense,
            mp=self.max_mp,
            level=self.level,
            exp=self.exp,    
            element=self.element,
            skills=new_skills,
            growth_type=self.growth_type,
            monster_id=self.monster_id, 
            image_filename=self.image_filename,
            rank=self.rank,
            speed=self.speed,  # speed 属性をコピー時に引き継ぐ
            drop_items=copy.deepcopy(self.drop_items),
            scout_rate=self.scout_rate,
            learnset=copy.deepcopy(self.learnset)
        )
        new_monster.max_hp = self.max_hp
        new_monster.hp = new_monster.max_hp
        new_monster.max_mp = self.max_mp
        new_monster.mp = new_monster.max_mp
        new_monster.is_alive = True 
        return new_monster
