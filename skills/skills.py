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
    # ------------------------------------------------------------
# バフ／デバフ用 効果関数サンプル  （必要に応じて Monster クラス側で管理）
# ------------------------------------------------------------
def increase_attack(monster, amount=5):
    monster.attack += amount
    def revert():
        monster.attack -= amount
    return revert

def increase_magic(monster, amount=5):
    monster.magic += amount
    def revert():
        monster.magic -= amount
    return revert

def decrease_defense(monster, amount=5):
    monster.defense -= amount
    def revert():
        monster.defense += amount
    return revert


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

# ------------------------------------------------------------
# 追加スキル定義
# ------------------------------------------------------------
# 1) 攻撃系 ──────────────────────────────────────────
thunder_bolt = Skill(
    "サンダーボルト",
    power=40,
    cost=6,
    skill_type="attack",
    effect="paralyze",
    description="雷撃で攻撃し、稀に麻痺させる",
    category="魔法",
)

ice_spear = Skill(
    "アイススピア",
    power=35,
    cost=6,
    skill_type="attack",
    effect="freeze",
    description="氷の槍で貫き、低確率で凍結させる",
    category="魔法",
)

wind_slash = Skill(
    "ウィンドスラッシュ",
    power=28,
    cost=4,
    skill_type="attack",
    description="鋭い風で切り裂く",
    category="物理",
)

earth_quake = Skill(
    "アースクエイク",
    power=30,
    cost=9,
    skill_type="attack",
    scope="all",
    description="大地を揺らし敵全体にダメージ",
    category="魔法",
)

dark_pulse = Skill(
    "ダークパルス",
    power=32,
    cost=6,
    skill_type="attack",
    effect="fear",
    description="闇の衝撃波で恐怖を与える",
    category="魔法",
)

holy_light = Skill(
    "ホーリーライト",
    power=38,
    cost=7,
    skill_type="attack",
    effect="blind",
    description="聖なる光でダメージ＆失明を狙う",
    category="魔法",
)

meteor_strike = Skill(
    "メテオストライク",
    power=50,
    cost=12,
    skill_type="attack",
    scope="all",
    description="隕石を落とし敵全体に大ダメージ",
    category="魔法",
)

poison_dart = Skill(
    "ポイズンダート",
    power=18,
    cost=2,
    skill_type="attack",
    effect="poison",
    description="毒針で攻撃し毒状態にする",
    category="物理",
)

blade_rush = Skill(
    "ブレードラッシュ",
    power=22,
    cost=3,
    skill_type="attack",
    description="連続斬りでランダム敵を数回攻撃",
    category="物理",
)

dragon_breath = Skill(
    "ドラゴンブレス",
    power=45,
    cost=10,
    skill_type="attack",
    effect="burn",
    scope="all",
    description="灼熱のブレスで敵全体を焼き払う",
    category="魔法",
)

# 2) 回復系 ──────────────────────────────────────────
cure = Skill(
    "キュア",
    power=40,
    cost=6,
    skill_type="heal",
    target="ally",
    description="味方1体を大きく回復",
    category="回復",
)

regen = Skill(
    "リジェネ",
    power=10,
    cost=5,
    skill_type="buff",
    target="ally",
    duration=4,
    effect="regen",          # 毎ターン回復フラグ等で管理
    description="数ターンかけて徐々に回復",
    category="回復",
)

revive = Skill(
    "リバイブ",
    power=999,               # 特殊扱い
    cost=15,
    skill_type="status",
    target="ally",
    effect="revive",
    description="戦闘不能の味方をHP半分で復活",
    category="回復",
)

# 3) バフ系 ──────────────────────────────────────────
power_up = Skill(
    "パワーアップ",
    power=0,
    cost=4,
    skill_type="buff",
    target="ally",
    duration=3,
    effect=increase_attack,
    description="攻撃力を上げる",
    category="補助",
)

magic_boost = Skill(
    "マジックブースト",
    power=0,
    cost=4,
    skill_type="buff",
    target="ally",
    duration=3,
    effect=increase_magic,
    description="魔力を上げる",
    category="補助",
)

speed_up = Skill(
    "スピードアップ",
    power=0,
    cost=3,
    skill_type="buff",
    target="ally",
    duration=3,
    effect="speed_up",
    description="素早さを上げる",
    category="補助",
)

brave_song = Skill(
    "ブレイブソング",
    power=0,
    cost=7,
    skill_type="buff",
    target="ally",
    scope="all",
    duration=3,
    effect="atk_def_up",
    description="戦意を高め味方全体の攻防を強化",
    category="補助",
)

# 4) デバフ系 ──────────────────────────────────────────
weaken_armor = Skill(
    "ウィークンアーマー",
    power=0,
    cost=5,
    skill_type="debuff",
    effect=decrease_defense,
    duration=3,
    description="敵の防御力を下げる",
    category="弱体",
)

slow = Skill(
    "スロウ",
    power=0,
    cost=4,
    skill_type="debuff",
    effect="slow",
    duration=3,
    description="敵の素早さを下げる",
    category="弱体",
)

silence = Skill(
    "サイレンス",
    power=0,
    cost=6,
    skill_type="debuff",
    effect="silence",
    duration=3,
    description="魔法を封じる",
    category="弱体",
)

curse = Skill(
    "カース",
    power=0,
    cost=8,
    skill_type="debuff",
    effect="curse",
    duration=4,
    description="呪いを付与し各種能力を低下",
    category="弱体",
)

# 5) 状態異常系（直接付与）─────────────────────────────
stun_blow = Skill(
    "スタンブロウ",
    power=20,
    cost=4,
    skill_type="attack",
    effect="stun",
    description="殴打して気絶させる",
    category="物理",
)

sleep_spell = Skill(
    "スリープ",
    power=0,
    cost=5,
    skill_type="status",
    effect="sleep",
    description="敵を眠らせる魔法",
    category="魔法",
)

paralysis_shock = Skill(
    "パラライズショック",
    power=25,
    cost=5,
    skill_type="attack",
    effect="paralyze",
    description="痺れる衝撃で麻痺付与",
    category="魔法",
)

confusion_gas = Skill(
    "コンフュージョンガス",
    power=0,
    cost=6,
    skill_type="status",
    scope="all",
    effect="confuse",
    description="混乱ガスで敵全体を混乱させる",
    category="魔法",
)

# ------------------------------------------------------------
# ALL_SKILLS に追加（既存辞書の下で実行）
# ------------------------------------------------------------
ALL_SKILLS.update({
    # 攻撃
    "thunder_bolt": thunder_bolt,
    "ice_spear": ice_spear,
    "wind_slash": wind_slash,
    "earth_quake": earth_quake,
    "dark_pulse": dark_pulse,
    "holy_light": holy_light,
    "meteor_strike": meteor_strike,
    "poison_dart": poison_dart,
    "blade_rush": blade_rush,
    "dragon_breath": dragon_breath,
    # 回復
    "cure": cure,
    "regen": regen,
    "revive": revive,
    # バフ
    "power_up": power_up,
    "magic_boost": magic_boost,
    "speed_up": speed_up,
    "brave_song": brave_song,
    # デバフ
    "weaken_armor": weaken_armor,
    "slow": slow,
    "silence": silence,
    "curse": curse,
    # 状態異常
    "stun_blow": stun_blow,
    "sleep_spell": sleep_spell,
    "paralysis_shock": paralysis_shock,
    "confusion_gas": confusion_gas,
})
