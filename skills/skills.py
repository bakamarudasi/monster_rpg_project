class Skill:
    def __init__(self, name, power, cost=0, skill_type="attack", effect=None, target="enemy", scope="single"):
        """
        :param name: スキル名
        :param power: 威力（攻撃なら攻撃力に加算、回復なら回復量）
        :param cost: 使用コスト（MPやTPなどを導入する場合）
        :param skill_type: "attack", "heal", "buff", "debuff", "status"
        :param effect: 特殊効果（関数や状態異常名など）
        :param target: "enemy" or "ally"（対象指定）
        :param scope: "single" or "all"（単体か全体か）
        """
        self.name = name
        self.power = power
        self.cost = cost
        self.skill_type = skill_type
        self.effect = effect
        self.target = target
        self.scope = scope

    def describe(self):
        scope_text = "全体" if self.scope == "all" else "単体"
        return f"{self.name} (Type: {self.skill_type}, Power: {self.power}, {scope_text})"
# 攻撃スキル
fireball = Skill("ファイアボール", power=30, skill_type="attack", effect="burn")

# 回復スキル
heal = Skill("ヒール", power=25, skill_type="heal", target="ally")
mass_heal = Skill("ヒールオール", power=15, skill_type="heal", target="ally", scope="all")

# バフスキル
def increase_defense(monster):
    monster.defense += 5

guard_up = Skill("ガードアップ", power=0, skill_type="buff", effect=increase_defense, target="ally")

ALL_SKILLS = {
    "fireball": fireball,
    "heal": heal,
    "guard_up": guard_up,
    "mass_heal": mass_heal,
    # 新しいスキルを追加したら、ここにも追記していきます
    # "thunder_bolt": thunder_bolt, # 例えば
}