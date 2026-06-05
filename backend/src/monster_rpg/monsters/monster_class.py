from ..skills.skills import ALL_SKILLS
import copy  # deepcopyのためにインポート
import uuid # uuidのためにインポート
import random
from .evolution_rules import EVOLUTION_RULES
from .personality import (
    DEFAULT_PERSONALITY_ID,
    IV_STATS,
    IV_LABELS,
    IV_MAX,
    IV_GROWTH_STRENGTH,
    get_personality,
    get_trait,
    talent_from_ivs,
    iv_judge_label,
    iv_total,
    iv_max_total,
    normalize_ivs,
    random_personality_id,
    random_ivs,
    roll_trait_for_talent,
    zero_ivs,
)

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
    # MP は全成長型で伸ばす（skills を使い続けられるように）。魔力は控えめに全型へ。
    mp_gain = 2 + (current_level // 8)
    magic_gain = 1 + (current_level // 12)
    return {
        "hp": hp_gain,
        "mp": mp_gain,
        "attack": attack_gain,
        "defense": defense_gain,
        "magic": magic_gain,
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
        "mp": 2 + (current_level // 8),
        "attack": attack_gain,
        "defense": defense_gain,
        "magic": 1 + (current_level // 12),
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
        "mp": 2 + (current_level // 8),
        "attack": attack_gain,
        "defense": defense_gain,
        "magic": 1 + (current_level // 12),
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
        magic=0,
        drop_items=None,
        scout_rate=0.25,
        ai_role="attacker",
        learnset=None,
        skill_sequence=None,
        unit_id=None,
        atb_gauge=0
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
        # 魔力パラメータ。魔法スキルの威力計算に使う（魔法型は初期値を持つ）
        self.base_magic = magic

        # 一時的な補正値と倍率
        self._stat_bonuses = {"attack": 0, "defense": 0, "speed": 0, "magic": 0}
        self._stat_multipliers = {"attack": 1.0, "defense": 1.0, "speed": 1.0, "magic": 1.0}
        # 永続的な強化（種アイテム・配合の累代＋値などで恒久的に加算される）
        self.permanent_bonuses = {"attack": 0, "defense": 0, "speed": 0, "magic": 0}
        # 配合の世代（＋値）。配合を重ねるほど増え、ステータスに加算される
        self.plus_value = 0
        # レア個体（★）フラグ。配合のレア抽選で生まれた個体は能力が底上げされる
        self.is_rare = False
        # 個体の個性。性格＝ステ傾向（派生4ステの倍率）、個体値＝ステ別の隠し数値
        # (0〜31)でレベルに比例して成長率に効く。才能ランクは個体値から導出する。
        # is_rare/plus_value の「強さ」とは別軸で、良個体を狙う配合の動機になる。
        self.personality_id = DEFAULT_PERSONALITY_ID
        self.ivs = zero_ivs()
        # 個体値の数値を鑑定済みか（未鑑定なら数値は伏せる）。才能ランクは常時表示。
        self.iv_appraised = False
        # 固有特性（鬼才で確定、天才で抽選）。None なら特性なし。
        self.trait_id = None
        # 個体値による成長の端数を貯めるバンク（小さな取得量でも倍率を取りこぼさない）
        self._growth_bank = {s: 0.0 for s in IV_STATS}

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
        self.equipment_slots = ["weapon", "armor", "helmet", "accessory", "boots"]
        self.learnset = learnset if learnset else {}
        self.skill_sequence = skill_sequence if skill_sequence else []
        self.unit_id = unit_id if unit_id is not None else str(uuid.uuid4()) # Add unit_id attribute
        self.atb_gauge = atb_gauge # ATBゲージの初期値
        # バリア（シールド）。HPの手前でダメージを肩代わりする一時的な盾。
        self.shield = 0
        # 耐性: 受けやすさ係数（1.0=通常, 0.5=半減, 0.0=無効）。種族固有＋装備で合算。
        self.status_resist: dict[str, float] = {}
        self.element_resist: dict[str, float] = {}
        # ボス個体フラグ。登場演出やUIの強調に使う。
        self.is_boss = False
        # ロック：合成/リリースから保護する（大事な個体の事故防止）
        self.locked = False

    def update_atb_gauge(self, amount: int | None = None) -> None:
        """ATBゲージを更新する。amountが指定されなければ素早さに応じて増加。"""
        if amount is None:
            self.atb_gauge += self.speed
        else:
            self.atb_gauge += amount
        self.atb_gauge = min(100, self.atb_gauge) # ゲージは最大100

    def reset_atb_gauge(self) -> None:
        """ATBゲージをリセットする。"""
        self.atb_gauge = 0

    # ------------------------------------------------------------------
    # Individuality (personality / talent)
    # ------------------------------------------------------------------
    @property
    def personality(self):
        """この個体の性格（ステ傾向）。未知IDはバランス型にフォールバック。"""
        return get_personality(self.personality_id)

    @property
    def talent(self):
        """この個体の才能（個体値の総合評価ランク）。個体値から導出する。"""
        return talent_from_ivs(self.ivs)

    @property
    def trait(self):
        """この個体の固有特性（無ければ None）。"""
        return get_trait(self.trait_id)

    def has_trait_effect(self, effect: str) -> bool:
        t = self.trait
        return t is not None and t.effect == effect

    def _individual_multiplier(self, stat: str) -> float:
        """性格による派生ステの恒久倍率。バランス型なら 1.0（=従来通り）。

        個体値は倍率ではなく成長率（level_up の取得量）に効くので、ここには乗せない。
        """
        return 1.0 + self.personality.modifiers.get(stat, 0.0)

    def roll_individuality(self) -> None:
        """性格・個体値・固有特性をランダムに引き直す（野生個体の生成時などに使う）。"""
        self.personality_id = random_personality_id()
        self.ivs = random_ivs()
        # 固有特性は才能（個体値）が高い個体にだけ宿る。野生では稀。
        self.trait_id = roll_trait_for_talent(self.talent.id)

    def appraise(self) -> None:
        """個体値の数値を開示済みにする（鑑定）。"""
        self.iv_appraised = True

    def _iv_growth_increase(self, stat: str, base_gain: int) -> int:
        """個体値に応じてレベルアップ取得量を底上げし、端数はバンクに繰り越す。

        個体値0なら ``base_gain`` をそのまま返す（＝従来挙動と完全互換）。
        """
        iv = int(self.ivs.get(stat, 0) or 0)
        bank = self._growth_bank
        bank[stat] = bank.get(stat, 0.0) + base_gain * (1.0 + iv / IV_MAX * IV_GROWTH_STRENGTH)
        take = int(bank[stat])
        bank[stat] -= take
        return take

    def individuality_summary(self) -> dict:
        """UI / シリアライズ用に性格・才能・個体値をまとめた辞書を返す。

        性格と才能ランクは常時表示。個体値の数値は鑑定済みのときだけ含める。
        """
        p = self.personality
        t = self.talent
        trait = self.trait
        summary = {
            "personality": {"id": p.id, "name": p.name, "effect": p.effect_text},
            "talent": {"id": t.id, "name": t.name, "hidden": t.hidden},
            "trait": {"id": trait.id, "name": trait.name, "description": trait.description} if trait else None,
            "appraised": bool(self.iv_appraised),
        }
        if self.iv_appraised:
            summary["ivs"] = {
                s: {"value": int(self.ivs.get(s, 0) or 0), "label": iv_judge_label(self.ivs.get(s, 0))}
                for s in IV_STATS
            }
            summary["iv_total"] = iv_total(self.ivs)
            summary["iv_max"] = iv_max_total()
        return summary

    # ------------------------------------------------------------------
    # Derived stat properties
    # ------------------------------------------------------------------
    @property
    def attack(self) -> int:
        base = self.base_attack + self._stat_bonuses.get("attack", 0) + self.permanent_bonuses.get("attack", 0)
        total = base + self._equipment_bonus("attack")
        return int(total * self._stat_multipliers.get("attack", 1.0) * self._individual_multiplier("attack"))

    @attack.setter
    def attack(self, value: int) -> None:
        self.base_attack = value

    @property
    def defense(self) -> int:
        base = self.base_defense + self._stat_bonuses.get("defense", 0) + self.permanent_bonuses.get("defense", 0)
        total = base + self._equipment_bonus("defense")
        return int(total * self._stat_multipliers.get("defense", 1.0) * self._individual_multiplier("defense"))

    @defense.setter
    def defense(self, value: int) -> None:
        self.base_defense = value

    @property
    def speed(self) -> int:
        base = self.base_speed + self._stat_bonuses.get("speed", 0) + self.permanent_bonuses.get("speed", 0)
        total = base + self._equipment_bonus("speed")
        return int(total * self._stat_multipliers.get("speed", 1.0) * self._individual_multiplier("speed"))

    @speed.setter
    def speed(self, value: int) -> None:
        self.base_speed = value

    @property
    def magic(self) -> int:
        base = self.base_magic + self._stat_bonuses.get("magic", 0) + self.permanent_bonuses.get("magic", 0)
        total = base + self._equipment_bonus("magic")
        return int(total * self._stat_multipliers.get("magic", 1.0) * self._individual_multiplier("magic"))

    @magic.setter
    def magic(self, value: int) -> None:
        self.base_magic = value

    def add_permanent_stat(self, stat: str, amount: int) -> int:
        """種アイテム等で恒久的にステータスを上げる。HP/MPは最大値に直接加算する。"""
        amount = int(amount)
        if stat in ("hp", "max_hp"):
            self.max_hp += amount
            self.hp = min(self.max_hp, self.hp + amount)
            return amount
        if stat in ("mp", "max_mp"):
            self.max_mp += amount
            self.mp = min(self.max_mp, self.mp + amount)
            return amount
        if stat in self.permanent_bonuses:
            self.permanent_bonuses[stat] += amount
            return amount
        return 0

    def add_plus_value(self, amount: int = 1) -> None:
        """配合の世代（＋値）を加算し、相応のステータス補正を恒久付与する。"""
        amount = max(0, int(amount))
        if amount <= 0:
            return
        self.plus_value += amount
        self.permanent_bonuses["attack"] += amount
        self.permanent_bonuses["defense"] += amount
        self.permanent_bonuses["speed"] += amount
        self.max_hp += 2 * amount
        self.max_mp += amount
        self.hp = min(self.max_hp, self.hp)
        self.mp = min(self.max_mp, self.mp)

    def make_rare_individual(self) -> None:
        """★レア個体化：基礎能力の約30%を恒久ボーナスとして上乗せする。

        合成のレア個体抽選と、進化の覚醒抽選の両方から使われる共通処理。
        """
        self.is_rare = True
        for stat in ("attack", "defense", "speed", "magic"):
            base = getattr(self, f"base_{stat}", 0)
            self.permanent_bonuses[stat] = self.permanent_bonuses.get(stat, 0) + max(1, round(base * 0.3))
        self.max_hp += max(5, round(self.max_hp * 0.3))
        self.max_mp += max(2, round(self.max_mp * 0.3))
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.add_plus_value(2)

    def _has_equipment(self, key: str) -> bool:
        """指定の equip_id もしくはカテゴリの装備を装備中か（触媒進化の条件用）。"""
        for eq in getattr(self, "equipment", {}).values():
            base = getattr(eq, "base_item", eq)
            if getattr(base, "equip_id", None) == key or getattr(base, "category", None) == key:
                return True
        return False

    def show_status(self, log: list[dict[str, str]] | None):
        if log is None:
            return
        log.append({'type': 'info', 'message': f"名前: {self.name} (ID: {self.monster_id}, Lv.{self.level}, Rank: {self.rank})"})
        talent = self.talent
        talent_txt = talent.name + ("（隠し才能）" if talent.hidden else "")
        log.append({'type': 'info', 'message': f"性格: {self.personality.name}（{self.personality.effect_text}） / 才能: {talent_txt}"})
        if self.trait is not None:
            log.append({'type': 'info', 'message': f"固有特性: {self.trait.name}（{self.trait.description}）"})
        if self.iv_appraised:
            iv_txt = " ".join(
                f"{IV_LABELS[s]}:{int(self.ivs.get(s, 0) or 0)}({iv_judge_label(self.ivs.get(s, 0))})"
                for s in IV_STATS
            )
            log.append({'type': 'info', 'message': f"個体値 {iv_txt}"})
        if self.element:
            log.append({'type': 'info', 'message': f"属性: {self.element}"})
        log.append({'type': 'info', 'message': f"HP: {self.hp}/{self.max_hp}"})
        log.append({'type': 'info', 'message': f"MP: {self.mp}/{self.max_mp}"})
        log.append({'type': 'info', 'message': f"攻撃力: {self.attack}"})
        log.append({'type': 'info', 'message': f"防御力: {self.defense}"})
        log.append({'type': 'info', 'message': f"魔力: {self.magic}"})
        log.append({'type': 'info', 'message': f"素早さ: {self.speed}"}) # 素早さを表示
        exp_needed = self.calculate_exp_to_next_level()
        log.append({'type': 'info', 'message': f"経験値: {self.exp}/{exp_needed if exp_needed is not None else 'N/A'}"})
        if self.skills:
            log.append({'type': 'info', 'message': "スキル:"})
            for skill_obj in self.skills:
                if hasattr(skill_obj, 'describe') and callable(skill_obj.describe):
                    log.append({'type': 'info', 'message': f"  - {skill_obj.describe()}"})
                else:
                    log.append({'type': 'info', 'message': f"  - {skill_obj.name}"})
        else:
            log.append({'type': 'info', 'message': "  (スキルなし)"})
        if self.status_effects:
            effect_names = ", ".join(effect['name'] for effect in self.status_effects)
            log.append({'type': 'info', 'message': f"状態異常: {effect_names}"})
        log.append({'type': 'info', 'message': "-" * 20})

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
    def heal(self, stat: str, amount, log: list[dict[str, str]] | None = None):
        if log is None:
            log = []
        if stat == 'hp':
            if amount == 'full':
                self.hp = self.max_hp
                log.append({'type': 'info', 'message': f"{self.name} のHPが全回復した！"})
            else:
                before = self.hp
                self.hp = min(self.max_hp, self.hp + int(amount))
                healed = self.hp - before
                if healed:
                    log.append({'type': 'info', 'message': f"{self.name} のHPが {healed} 回復した！ (HP: {self.hp})"})
        elif stat == 'mp':
            if amount == 'full':
                self.mp = self.max_mp
                log.append({'type': 'info', 'message': f"{self.name} のMPが全回復した！"})
            else:
                before = self.mp
                self.mp = min(self.max_mp, self.mp + int(amount))
                restored = self.mp - before
                if restored:
                    log.append({'type': 'info', 'message': f"{self.name} のMPが {restored} 回復した！ (MP: {self.mp})"})

    def _equipment_resist(self, kind: str, key: str) -> float:
        """装備が持つ耐性係数を掛け合わせて返す（kind は 'status_resist' / 'element_resist'）。"""
        factor = 1.0
        for e in self.equipment.values():
            base = getattr(e, "base_item", e)  # EquipmentInstance なら素装備を見る
            table = getattr(base, kind, None)
            if table and key in table:
                factor *= float(table[key])
        return factor

    def status_resistance(self, name: str) -> float:
        """状態異常 name の受けやすさ係数（種族固有×装備）。0.0 で無効。"""
        factor = float(self.status_resist.get(name, 1.0)) * self._equipment_resist("status_resist", name)
        return max(0.0, factor)

    def element_damage_factor(self, attacker_element: str | None) -> float:
        """attacker_element 属性ダメージの被ダメ係数（種族固有×装備）。0.0 で無効。"""
        if not attacker_element:
            return 1.0
        factor = float(self.element_resist.get(attacker_element, 1.0)) * self._equipment_resist("element_resist", attacker_element)
        return max(0.0, factor)

    def absorb_with_shield(self, damage: int, log: list[dict[str, str]] | None = None) -> int:
        """バリアでダメージを肩代わりし、HPに通す残りダメージを返す。

        バリアが無い (shield == 0) ときは ``damage`` をそのまま返し、ログも残さない
        ので、既存のダメージ処理の挙動は一切変わらない。
        """
        if log is None:
            log = []
        shield = getattr(self, "shield", 0)
        if shield > 0 and damage > 0:
            absorbed = min(shield, damage)
            self.shield = shield - absorbed
            damage -= absorbed
            log.append({'type': 'info', 'message': f"{self.name} のバリアが {absorbed} ダメージを防いだ！ (残りバリア: {self.shield})"})
        return damage

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

    def apply_status(self, name: str, log_or_duration=None, duration: int | None = None) -> None:
        """Apply a status to this monster.

        The second argument may be a log list for backwards compatibility or a
        duration value when called with two positional arguments in tests.
        """
        from ..battle import apply_status

        log: list[dict[str, str]] | None
        if isinstance(log_or_duration, list):
            log = log_or_duration
        elif isinstance(log_or_duration, int) and duration is None:
            duration = log_or_duration
            log = []
        else:
            log = log_or_duration

        apply_status(self, name, log, duration)

    def cure_status(self, name: str, log: list[dict[str, str]]) -> None:
        before = len(self.status_effects)
        self.status_effects = [e for e in self.status_effects if e['name'] != name]
        if len(self.status_effects) < before:
            log.append({'type': 'info', 'message': f"{self.name} の {name} が治った。"})

    @property
    def total_skills(self):
        skills = self.skills[:]
        # 装備が付与するスキルを足す。覚えているスキルや別装備と名前が被るものは除く
        seen = {getattr(s, 'name', None) for s in skills}
        for e in self.equipment.values():
            for gs in getattr(e, 'granted_skills', []) or []:
                nm = getattr(gs, 'name', None)
                if nm not in seen:
                    skills.append(gs)
                    seen.add(nm)
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

    def _try_evolution(self, log: list[dict[str, str]] | None = None, verbose=True):
        """進化分岐を評価し、最初に条件を満たす枝へ進化する（覚醒抽選つき）。

        戻り値は進化したとき reveal 用の dict、しなければ None。
        """
        from .evolution_rules import get_evolution_branches
        from .monster_data import ALL_MONSTERS  # local import to avoid cycle

        for branch in get_evolution_branches(self.monster_id):
            if self.level < branch.get('level', 0):
                continue
            req_skill = branch.get('requires_skill')
            if req_skill and not any(getattr(s, 'name', '') == req_skill for s in self.skills):
                continue
            req_equip = branch.get('requires_equipment')
            if req_equip and not self._has_equipment(req_equip):
                continue

            # 覚醒抽選：当たると★レア個体化し、awaken_into があればさらに上位種へ
            awakened = random.random() < float(branch.get('awaken_chance', 0) or 0)
            target_id = branch.get('awaken_into') if (awakened and branch.get('awaken_into')) else branch.get('evolves_to')
            template = ALL_MONSTERS.get(target_id) or ALL_MONSTERS.get(branch.get('evolves_to'))
            if not template:
                continue

            evolved = template.copy()
            evolved.level = self.level
            evolved.exp = self.exp
            evolved.equipment = getattr(self, 'equipment', {}).copy()
            # 個体の個性（性格・個体値・鑑定状態・固有特性・成長バンク）は進化後も維持する。
            # 個体値は成長率に効くため、ここで引き継がないと進化のたびに育ちがリセットされる。
            evolved.personality_id = self.personality_id
            evolved.ivs = dict(self.ivs)
            evolved.iv_appraised = self.iv_appraised
            evolved.trait_id = self.trait_id
            evolved._growth_bank = dict(self._growth_bank)
            self.__dict__.update(evolved.__dict__)
            if awakened:
                self.make_rare_individual()

            if verbose and log is not None:
                if awakened:
                    log.append({'type': 'info', 'message': f"✨覚醒進化！ ★{template.name} になった！"})
                else:
                    log.append({'type': 'info', 'message': f"{template.name} に進化した！"})
            return {'evolved_to': self.monster_id, 'name': template.name,
                    'awakened': awakened, 'became_rare': awakened}
        return None

    def _learn_skills_for_level(self, log: list[dict[str, str]] | None = None, verbose=True):
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
                msg = f"{self.name} は {template.name} を覚えた！"
                if log is not None:
                    log.append({'type': 'info', 'message': msg})
                print(msg)

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

    def gain_exp(self, amount, log: list[dict[str, str]] | None = None, verbose=True):
        if not self.is_alive:
            return

        # 固有特性「速学」: 獲得経験値を底上げする。
        trait = self.trait
        if trait is not None and trait.effect == "exp" and amount > 0:
            amount = int(amount * (1.0 + trait.value))

        self.exp += amount
        if verbose:
            msg = f"{self.name} は {amount} の経験値を獲得した！ (現在EXP: {self.exp})"
            if log is not None:
                log.append({'type': 'info', 'message': msg})
            print(msg)

        exp_needed_for_next_level = self.calculate_exp_to_next_level()
        if exp_needed_for_next_level is None:
            return

        while self.exp >= exp_needed_for_next_level and self.is_alive:
            self.exp -= exp_needed_for_next_level
            self.level_up(log=log, verbose=verbose)

            exp_needed_for_next_level = self.calculate_exp_to_next_level()
            if exp_needed_for_next_level is None:
                break

        if self.exp < 0:
            self.exp = 0

    def level_up(self, log: list[dict[str, str]] | None = None, verbose=True):
        self.level += 1
        if verbose:
            msg = f"🎉🎉🎉 {self.name} は レベル {self.level} に上がった！ 🎉🎉"
            if log is not None:
                log.append({'type': 'info', 'message': msg})
            print(msg)

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
            if verbose and log is not None:
                log.append({'type': 'warning', 'message': f"警告: 未知の成長タイプ '{self.growth_type}' が指定されました。平均型として計算します。"})
            status_gains_dict = get_status_gains_average(self.level)
        
        if not isinstance(status_gains_dict, dict):
            status_gains_dict = {}

        status_gains_dict.setdefault("hp", 0)
        status_gains_dict.setdefault("mp", 0)
        status_gains_dict.setdefault("attack", 0)
        status_gains_dict.setdefault("defense", 0)
        status_gains_dict.setdefault("magic", 0)
        status_gains_dict.setdefault("speed", 0)

        # 個体値（IV）でレベルアップ取得量を底上げする。HPを含む5ステが対象、MPは対象外。
        # 端数はバンクに繰り越し、個体値が高いほどレベルを重ねるほど差が開く＝成長率。
        hp_increase = self._iv_growth_increase("hp", status_gains_dict["hp"])
        mp_increase = status_gains_dict["mp"]
        attack_increase = self._iv_growth_increase("attack", status_gains_dict["attack"])
        defense_increase = self._iv_growth_increase("defense", status_gains_dict["defense"])
        magic_increase = self._iv_growth_increase("magic", status_gains_dict["magic"])
        speed_increase = self._iv_growth_increase("speed", status_gains_dict["speed"])

        self.max_hp += hp_increase
        self.hp = self.max_hp
        self.base_attack += attack_increase
        self.base_defense += defense_increase
        self.base_speed += speed_increase
        self.max_mp += mp_increase
        self.mp = self.max_mp
        self.base_magic += magic_increase

        if verbose:
            msg = (
                f"最大HPが {hp_increase}、最大MPが {mp_increase}、攻撃力が {attack_increase}、"
                f"防御力が {defense_increase}、魔力が {magic_increase}、素早さが {speed_increase} 上昇した！"
            )
            if log is not None:
                log.append({'type': 'info', 'message': msg})
            print(msg)

        self._try_evolution(log=log, verbose=verbose)
        self._learn_skills_for_level(log=log, verbose=verbose)

    def advance_to_level(self, target_level, verbose=False):
        """Raise this monster's level until reaching target_level."""
        while self.level < target_level and self.is_alive:
            self.level_up(verbose=verbose)

    def to_dict(self):
        return {
            'name': self.name,
            'monster_id': self.monster_id,
            'level': self.level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'atb_gauge': self.atb_gauge,
            'shield': self.shield,
            'alive': self.is_alive,
            'image_filename': self.image_filename,
            'statuses': [{'name': s['name'], 'remaining': s['remaining']} for s in self.status_effects],
            'unit_id': self.unit_id,
            'individuality': self.individuality_summary(),
        }

    @classmethod
    def from_dict(cls, data):
        monster = cls(
            name=data['name'],
            hp=data['max_hp'], # Use max_hp to initialize current hp
            attack=data['attack'],
            defense=data['defense'],
            mp=data['max_mp'], # Use max_mp to initialize current mp
            level=data['level'],
            monster_id=data['monster_id'],
            image_filename=data['image_filename'],
            speed=data['speed'],
            unit_id=data['unit_id'],
            atb_gauge=data['atb_gauge']
        )
        monster.hp = data['hp'] # Set current hp
        monster.mp = data['mp'] # Set current mp
        monster.is_alive = data['alive']
        monster.status_effects = data['statuses']
        monster.shield = data.get('shield', 0)
        return monster

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
            learnset=copy.deepcopy(self.learnset),
            unit_id=self.unit_id,
            atb_gauge=self.atb_gauge
        )
        new_monster.max_hp = self.max_hp
        new_monster.hp = new_monster.max_hp
        new_monster.max_mp = self.max_mp
        new_monster.mp = new_monster.max_mp
        new_monster.base_magic = self.base_magic
        new_monster.permanent_bonuses = dict(self.permanent_bonuses)
        new_monster.plus_value = self.plus_value
        new_monster.is_rare = self.is_rare
        new_monster.personality_id = self.personality_id
        new_monster.ivs = dict(self.ivs)
        new_monster.iv_appraised = self.iv_appraised
        new_monster.trait_id = self.trait_id
        new_monster._growth_bank = dict(self._growth_bank)
        new_monster.is_alive = True
        new_monster.skill_sequence = self.skill_sequence[:]
        new_monster.equipment = copy.deepcopy(self.equipment)
        new_monster.equipment_slots = self.equipment_slots[:]
        new_monster.status_resist = dict(self.status_resist)
        new_monster.element_resist = dict(self.element_resist)
        new_monster.is_boss = self.is_boss
        new_monster.locked = self.locked
        return new_monster
