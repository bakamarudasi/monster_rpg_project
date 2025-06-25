from ..skills.skills import ALL_SKILLS
import copy  # deepcopyのためにインポート
from .evolution_rules import EVOLUTION_RULES

GROWTH_TYPE_AVERAGE = "平均型"
GROWTH_TYPE_EARLY = "早熟型"
GROWTH_TYPE_LATE = "大器晩成型"
GROWTH_TYPE_POWER = "パワー型"
GROWTH_TYPE_MAGIC = "魔法型"
GROWTH_TYPE_DEFENSE = "防御型"
GROWTH_TYPE_SPEED = "スピード型"

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

def get_status_gains_power(current_level):
    base = get_status_gains_average(current_level)
    base["attack"] += 2 + (current_level // 5)
    return base

def get_status_gains_magic(current_level):
    base = get_status_gains_average(current_level)
    base["mp"] = base.get("mp", 0) + 3 + (current_level // 4)
    base["magic"] = base.get("magic", 0) + 2 + (current_level // 5)
    return base

def get_status_gains_defense(current_level):
    base = get_status_gains_average(current_level)
    base["defense"] += 2 + (current_level // 5)
    return base

def get_status_gains_speed(current_level):
    base = get_status_gains_average(current_level)
    base["speed"] += 2 + (current_level // 5)
    return base

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
    def __init__(
        self,
        name,
        hp,
        attack,
        defense,
        mp=30,
        level=1,
        exp=0,
        element=None,
        skills=None,
        growth_type=GROWTH_TYPE_AVERAGE,
        monster_id=None,
        family=None,
        image_filename=None,
        rank=RANK_D,
        speed=5,
        drop_items=None,
        scout_rate=0.25,
        ai_role="attacker",
        learnset=None,
        skill_sequence=None,
    ):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp

        # 基本ステータスを保持し、装備やバフによる補正は別管理とする
        self.base_attack = attack
        self.base_defense = defense
        self.base_speed = speed
        # 魔力パラメータ。魔法に関するバフ等で利用される
        self.base_magic = 0

        # 一時的な補正値と倍率
        self._stat_bonuses = {"attack": 0, "defense": 0, "speed": 0, "magic": 0}
        self._stat_multipliers = {"attack": 1.0, "defense": 1.0, "speed": 1.0, "magic": 1.0}

        self.level = level
        self.exp = exp
        self.element = element
        self.skills = skills if skills else []
        self.status_effects = []
        self.is_alive = True
        self.growth_type = growth_type
        self.family = family
        
        if monster_id is not None and isinstance(monster_id, str) and monster_id.strip() != "":
            self.monster_id = monster_id
        else:
            self.monster_id = name.lower()
        
        self.image_filename = image_filename
        self.rank = rank
        self.drop_items = drop_items if drop_items else []
        self.scout_rate = scout_rate  # スカウト成功率(0.0-1.0)
        self.ai_role = ai_role
        # 装備品スロット (weapon, armor など)。UI 表示のためスロットの一覧も保持
        self.equipment = {}
        self.equipment_slots = ["weapon", "armor", "accessory"]
        self.learnset = learnset if learnset else {}
        self.skill_sequence = skill_sequence if skill_sequence else []

    # ------------------------------------------------------------------
    # Derived stat properties
    # ------------------------------------------------------------------
    @property
    def attack(self) -> int:
        base = self.base_attack + self._stat_bonuses.get("attack", 0)
        total = base + self._equipment_bonus("attack")
        return int(total * self._stat_multipliers.get("attack", 1.0))

    @attack.setter
    def attack(self, value: int) -> None:
        self.base_attack = value

    @property
    def defense(self) -> int:
        base = self.base_defense + self._stat_bonuses.get("defense", 0)
        total = base + self._equipment_bonus("defense")
        return int(total * self._stat_multipliers.get("defense", 1.0))

    @defense.setter
    def defense(self, value: int) -> None:
        self.base_defense = value

    @property
    def speed(self) -> int:
        base = self.base_speed + self._stat_bonuses.get("speed", 0)
        total = base + self._equipment_bonus("speed")
        return int(total * self._stat_multipliers.get("speed", 1.0))

    @speed.setter
    def speed(self, value: int) -> None:
        self.base_speed = value

    @property
    def magic(self) -> int:
        base = self.base_magic + self._stat_bonuses.get("magic", 0)
        total = base + self._equipment_bonus("magic")
        return int(total * self._stat_multipliers.get("magic", 1.0))

    @magic.setter
    def magic(self, value: int) -> None:
        self.base_magic = value

    def show_status(self):
        print(f"名前: {self.name} (ID: {self.monster_id}, Lv.{self.level}, Rank: {self.rank})") 
        if self.element:
            print(f"属性: {self.element}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"MP: {self.mp}/{self.max_mp}")
        print(f"攻撃力: {self.attack}")
        print(f"防御力: {self.defense}")
        print(f"魔力: {self.magic}")
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
        """Equip an Equipment or EquipmentInstance to this monster."""
        if equipment is None:
            return
        self.equipment[equipment.slot] = equipment

    def _equipment_bonus(self, stat: str) -> int:
        bonus = 0
        for e in self.equipment.values():
            attr = f'total_{stat}'
            if hasattr(e, attr):
                bonus += getattr(e, attr)
            else:
                bonus += getattr(e, stat, 0)
        return bonus

    def total_attack(self):
        return self.attack

    def total_defense(self):
        return self.defense

    def total_speed(self):
        return self.speed

    # ------------------------------------------------------------------
    # Effect helper methods
    # ------------------------------------------------------------------
    def heal(self, stat: str, amount):
        if stat == 'hp':
            if amount == 'full':
                self.hp = self.max_hp
            else:
                before = self.hp
                self.hp = min(self.max_hp, self.hp + int(amount))
                healed = self.hp - before
                if healed:
                    print(f"{self.name} のHPが {healed} 回復した！ (HP: {self.hp})")
        elif stat == 'mp':
            if amount == 'full':
                self.mp = self.max_mp
            else:
                before = self.mp
                self.mp = min(self.max_mp, self.mp + int(amount))
                restored = self.mp - before
                if restored:
                    print(f"{self.name} のMPが {restored} 回復した！ (MP: {self.mp})")

    def apply_buff(self, stat: str, amount: int, duration: int) -> None:
        if not stat:
            return
        self._stat_bonuses[stat] = self._stat_bonuses.get(stat, 0) + amount

        def revert(m: "Monster" = self, s: str = stat, a: int = amount) -> None:
            m._stat_bonuses[s] = m._stat_bonuses.get(s, 0) - a

        if duration > 0:
            self.status_effects.append({
                'name': f'buff_{stat}',
                'remaining': duration,
                'remove_func': revert,
            })

    def apply_buff_percent(self, stat: str, percent_amount: float, duration: int) -> None:
        if not stat:
            return
        bonus_multiplier = 1.0 + percent_amount
        self._stat_multipliers[stat] = self._stat_multipliers.get(stat, 1.0) * bonus_multiplier

        def revert(m: "Monster" = self, s: str = stat, bm: float = bonus_multiplier) -> None:
            m._stat_multipliers[s] = m._stat_multipliers.get(s, 1.0) / bm

        if duration > 0:
            self.status_effects.append({
                'name': f'buff_percent_{stat}',
                'remaining': duration,
                'remove_func': revert,
            })

    def apply_status(self, name: str, duration: int | None = None) -> None:
        from ..battle import apply_status
        apply_status(self, name, duration)

    def cure_status(self, name: str) -> None:
        before = len(self.status_effects)
        self.status_effects = [e for e in self.status_effects if e['name'] != name]
        if len(self.status_effects) < before:
            print(f"{self.name} の {name} が治った。")

    @property
    def total_skills(self):
        skills = self.skills[:]
        for e in self.equipment.values():
            if hasattr(e, 'granted_skills'):
                skills.extend(e.granted_skills)
        return skills

    def get_skill_details(self):
        """Return skill name and description for all skills this monster can use."""
        details = []
        for sk in self.total_skills:
            details.append({
                'name': getattr(sk, 'name', ''),
                'description': getattr(sk, 'description', '')
            })
        return details

    def _try_evolution(self, verbose=True):
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
        if verbose:
            print(f"{template.name} に進化した！")

    def _learn_skills_for_level(self, verbose=True):
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
            if verbose:
                print(f"{self.name} は {template.name} を覚えた！")

    def calculate_exp_to_next_level(self):
        if self.growth_type == GROWTH_TYPE_EARLY:
            exp_needed = calculate_exp_for_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            exp_needed = calculate_exp_for_late(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            exp_needed = calculate_exp_for_average(self.level)
        elif self.growth_type in (
            GROWTH_TYPE_POWER,
            GROWTH_TYPE_MAGIC,
            GROWTH_TYPE_DEFENSE,
            GROWTH_TYPE_SPEED,
        ):
            exp_needed = calculate_exp_for_average(self.level)
        else:
            print(f"警告: 未知の成長タイプ '{self.growth_type}' が指定されました。平均型として計算します。")
            exp_needed = calculate_exp_for_average(self.level)
        return exp_needed

    def gain_exp(self, amount, verbose=True):
        if not self.is_alive:
            return

        self.exp += amount
        if verbose:
            print(f"{self.name} は {amount} の経験値を獲得した！ (現在EXP: {self.exp})")

        exp_needed_for_next_level = self.calculate_exp_to_next_level()
        if exp_needed_for_next_level is None:
            return

        while self.exp >= exp_needed_for_next_level and self.is_alive:
            self.exp -= exp_needed_for_next_level
            self.level_up(verbose=verbose)

            exp_needed_for_next_level = self.calculate_exp_to_next_level()
            if exp_needed_for_next_level is None:
                break

        if self.exp < 0:
            self.exp = 0

    def level_up(self, verbose=True):
        self.level += 1
        if verbose:
            print(f"🎉🎉🎉 {self.name} は レベル {self.level} に上がった！ 🎉🎉")

        status_gains_dict = {}
        if self.growth_type == GROWTH_TYPE_EARLY:
            status_gains_dict = get_status_gains_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            status_gains_dict = get_status_gains_late(self.level)
        elif self.growth_type == GROWTH_TYPE_POWER:
            status_gains_dict = get_status_gains_power(self.level)
        elif self.growth_type == GROWTH_TYPE_MAGIC:
            status_gains_dict = get_status_gains_magic(self.level)
        elif self.growth_type == GROWTH_TYPE_DEFENSE:
            status_gains_dict = get_status_gains_defense(self.level)
        elif self.growth_type == GROWTH_TYPE_SPEED:
            status_gains_dict = get_status_gains_speed(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            status_gains_dict = get_status_gains_average(self.level)
        else:
            print(f"警告: 未知の成長タイプ '{self.growth_type}'。平均型のステータス上昇を適用します。")
            status_gains_dict = get_status_gains_average(self.level)
        
        if not isinstance(status_gains_dict, dict):
            status_gains_dict = {}

        status_gains_dict.setdefault("hp", 0)
        status_gains_dict.setdefault("mp", 0)
        status_gains_dict.setdefault("attack", 0)
        status_gains_dict.setdefault("defense", 0)
        status_gains_dict.setdefault("magic", 0)
        status_gains_dict.setdefault("speed", 0)

        hp_increase = status_gains_dict["hp"]
        mp_increase = status_gains_dict["mp"]
        attack_increase = status_gains_dict["attack"]
        defense_increase = status_gains_dict["defense"]
        magic_increase = status_gains_dict["magic"]
        speed_increase = status_gains_dict["speed"]
            
        self.max_hp += hp_increase
        self.hp = self.max_hp
        self.base_attack += attack_increase
        self.base_defense += defense_increase
        self.base_speed += speed_increase
        self.max_mp += mp_increase
        self.mp = self.max_mp
        self.base_magic += magic_increase

        if verbose:
            print(
                f"最大HPが {hp_increase}、最大MPが {mp_increase}、攻撃力が {attack_increase}、防御力が {defense_increase}、魔力が {magic_increase}、素早さが {speed_increase} 上昇した！"
            )

        self._try_evolution(verbose=verbose)
        self._learn_skills_for_level(verbose=verbose)

    def advance_to_level(self, target_level, verbose=False):
        """Raise this monster's level until reaching target_level."""
        while self.level < target_level and self.is_alive:
            self.level_up(verbose=verbose)

    def copy(self):
        new_skills = [copy.deepcopy(skill) for skill in self.skills]
        
        new_monster = Monster(
            name=self.name,
            hp=self.max_hp,
            attack=self.base_attack,
            defense=self.base_defense,
            mp=self.max_mp,
            level=self.level,
            exp=self.exp,
            element=self.element,
            skills=new_skills,
            growth_type=self.growth_type,
            monster_id=self.monster_id,
            family=self.family,
            image_filename=self.image_filename,
            rank=self.rank,
            speed=self.base_speed,  # speed 属性をコピー時に引き継ぐ
            drop_items=copy.deepcopy(self.drop_items),
            scout_rate=self.scout_rate,
            ai_role=self.ai_role,
            learnset=copy.deepcopy(self.learnset)
        )
        new_monster.max_hp = self.max_hp
        new_monster.hp = new_monster.max_hp
        new_monster.max_mp = self.max_mp
        new_monster.mp = new_monster.max_mp
        new_monster.base_magic = self.base_magic
        new_monster.is_alive = True
        new_monster.skill_sequence = self.skill_sequence[:]
        new_monster.equipment = copy.deepcopy(self.equipment)
        new_monster.equipment_slots = self.equipment_slots[:]
        return new_monster
