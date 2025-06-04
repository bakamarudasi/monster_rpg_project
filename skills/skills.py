class Skill:
    def __init__(self, name, power, cost=0, skill_type="attack", effect=None, target="enemy", scope="single", duration=0, description="", category=None):
        """
        :param name: スキル名
        :param power: 威力（攻撃なら攻撃力に加算、回復なら回復量）
        :param cost: 消費MP
        :param skill_type: "attack", "heal", "buff", "debuff", "status"
        :param effect: 特殊効果（関数や状態異常名など）
        :param target: "enemy" or "ally"（対象指定）
        :param scope: "single" or "all"（単体か全体か）
        :param duration: 効果持続ターン数（バフ等）
        :param description: 説明文
        :param category: スキル分類（物理/魔法など）
        """
        self.name = name
        self.power = power
        self.cost = cost
        self.skill_type = skill_type
        self.effect = effect
        self.target = target
        self.scope = scope
        self.duration = duration
        self.description = description
        self.category = category

    def describe(self):
        scope_text = "全体" if self.scope == "all" else "単体"
        cost_text = f"MP:{self.cost}" if self.cost else ""
        return f"{self.name} ({self.skill_type}, Pow:{self.power}, {cost_text} {scope_text})"

# 攻撃スキル
fireball = Skill(
    "ファイアボール",
    power=30,
    cost=5,
    skill_type="attack",
    effect="burn",
    description="火の玉で攻撃する",
    category="魔法",
)

# 回復スキル
heal = Skill(
    "ヒール",
    power=25,
    cost=4,
    skill_type="heal",
    target="ally",
    description="味方1体のHPを回復",
    category="回復",
)
mass_heal = Skill(
    "ヒールオール",
    power=15,
    cost=8,
    skill_type="heal",
    target="ally",
    scope="all",
    description="味方全体を回復",
    category="回復",
)

# バフスキル
def increase_defense(monster):
    monster.defense += 5
    def revert():
        monster.defense -= 5
    return revert

guard_up = Skill(
    "ガードアップ",
    power=0,
    cost=3,
    skill_type="buff",
    effect=increase_defense,
    target="ally",
    duration=3,
    description="数ターン防御力を上げる",
    category="補助",
)

ALL_SKILLS = {
    "fireball": fireball,
    "heal": heal,
    "guard_up": guard_up,
    "mass_heal": mass_heal,
    # 新しいスキルを追加したら、ここにも追記していきます
    # "thunder_bolt": thunder_bolt, # 例えば
}
