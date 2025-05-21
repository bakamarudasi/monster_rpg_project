from skills.skills import ALL_SKILLS

GROWTH_TYPE_AVERAGE = "平均型"
GROWTH_TYPE_EARLY = "早熟型"
GROWTH_TYPE_LATE = "大器晩成型"
# monsters/definitions.py (Monsterクラス定義の前など、経験値テーブル関数の近くが良いでしょう)

def get_status_gains_average(current_level):
    """平均型のレベルアップ時ステータス上昇量"""
    # 例: 以前の固定値上昇に少しレベル補正を加える
    hp_gain = 5 + (current_level // 5)  # 5レベルごとにHP上昇量が少し増える
    attack_gain = 2 + (current_level // 10)
    defense_gain = 2 + (current_level // 10)
    return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}

def get_status_gains_early(current_level):
    """早熟型のレベルアップ時ステータス上昇量"""
    if current_level <= 10: # Lv10までは大きく成長
        hp_gain = 8 + (current_level // 3)
        attack_gain = 3 + (current_level // 5)
        defense_gain = 3 + (current_level // 5)
    elif current_level <= 25: # Lv25まではそこそこ
        hp_gain = 4 + (current_level // 6)
        attack_gain = 1 + (current_level // 8)
        defense_gain = 1 + (current_level // 8)
    else: # Lv26以降は伸び悩む
        hp_gain = 3
        attack_gain = 1
        defense_gain = 1
    return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}

def get_status_gains_late(current_level):
    """大器晩成型のレベルアップ時ステータス上昇量"""
    if current_level <= 15: # Lv15までは伸びが悪い
        hp_gain = 3 + (current_level // 7)
        attack_gain = 1 + (current_level // 10)
        defense_gain = 1 + (current_level // 10)
    elif current_level <= 30: # Lv30までは平均的に
        hp_gain = 6 + (current_level // 5)
        attack_gain = 2 + (current_level // 8)
        defense_gain = 2 + (current_level // 8)
    else: # Lv31以降、急成長！
        hp_gain = 10 + (current_level // 4)
        attack_gain = 4 + (current_level // 6)
        defense_gain = 4 + (current_level // 6)
    return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}


def calculate_exp_for_average(current_level):
    """平均型の必要経験値"""
    # 例: 以前の計算式をベースに
    return (current_level ** 2) * 20 + 50

def calculate_exp_for_early(current_level):
    """早熟型の必要経験値"""
    # 例: 低レベルでは少なく、高レベルで急増するイメージ
    if current_level < 10:
        return (current_level ** 2) * 15 + 30  # 平均より少なめ
    elif current_level < 30:
        return (current_level ** 2) * 25 + 100 # 平均よりやや多め
    else:
        return (current_level ** 3) * 10 + 500 # さらに急増

def calculate_exp_for_late(current_level):
    """大器晩成型の必要経験値"""
    # 例: 低レベルでは多く、高レベルになるほど相対的に伸びが良くなるイメージ
    if current_level < 15:
        return (current_level ** 2) * 30 + 100 # 平均より多め
    else:
        return (current_level ** 2) * 20 + 50  # 平均型と同じか、やや緩やかに
class Monster:
    def __init__(self, name, hp, attack, defense, level=1, exp=0, element=None, skills=None,growth_type=GROWTH_TYPE_AVERAGE):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.level = level
        self.exp = exp
        self.element = element
        self.skills = skills if skills else []
        self.status_effects = [] # これは前回ユーザーが追加したものでしたね！
        self.is_alive = True     # これも！
        self.growth_type = growth_type  # 新しく属性として保持
        
    def show_status(self):
        print(f"名前: {self.name} (Lv.{self.level})")
        if self.element:
            print(f"属性: {self.element}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"攻撃力: {self.attack}")
        print(f"防御力: {self.defense}")
        # 次のレベルまでの経験値を表示すると分かりやすい
        exp_needed = self.calculate_exp_to_next_level()
        print(f"経験値: {self.exp}/{exp_needed}") # 現在の経験値 / 次のレベルに必要な経験値
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
            effect_names = ", ".join(self.status_effects)
            print(f"状態異常: {effect_names}")
        print("-" * 20)

    def calculate_exp_to_next_level(self):
        """成長タイプに応じて、次のレベルアップに必要な経験値を計算します。"""
        if self.growth_type == GROWTH_TYPE_EARLY:
            return calculate_exp_for_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            return calculate_exp_for_late(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            return calculate_exp_for_average(self.level)
        else: # 未知の成長タイプの場合は平均型として扱う (フォールバック)
            print(f"警告: 未知の成長タイプ '{self.growth_type}' が指定されました。平均型として計算します。")
            return calculate_exp_for_average(self.level)

    def gain_exp(self, amount):
        """経験値を獲得し、必要であればレベルアップ処理を呼び出します。"""
        if not self.is_alive: # 戦闘不能なら経験値は得られない
            return

        self.exp += amount
        print(f"{self.name} は {amount} の経験値を獲得した！")

        # レベルアップ判定
        exp_needed_for_next_level = self.calculate_exp_to_next_level()
        while self.exp >= exp_needed_for_next_level and self.is_alive: # 生きている間だけレベルアップ
            self.exp -= exp_needed_for_next_level # 次のレベルに必要な経験値を消費
            self.level_up()
            # レベルアップ後の次のレベルに必要な経験値を再計算
            exp_needed_for_next_level = self.calculate_exp_to_next_level()
            # 経験値がマイナスにならないように (繰り越し分がマイナスになることは通常ないが念のため)
            if self.exp < 0:
                self.exp = 0


    # monsters/definitions.py の Monster クラス内の level_up メソッドを修正

    def level_up(self):
        """レベルアップ処理を行います。ステータス上昇やスキル習得など。"""
        self.level += 1
        print(f"🎉🎉🎉 {self.name} は レベル {self.level} に上がった！ 🎉🎉🎉")

        # 成長タイプに応じたステータス上昇量を決定
        status_gains_dict = {} # 上昇量を格納する辞書
        if self.growth_type == GROWTH_TYPE_EARLY:
            status_gains_dict = get_status_gains_early(self.level)
        elif self.growth_type == GROWTH_TYPE_LATE:
            status_gains_dict = get_status_gains_late(self.level)
        elif self.growth_type == GROWTH_TYPE_AVERAGE:
            status_gains_dict = get_status_gains_average(self.level)
        else: # 未知の成長タイプの場合は平均型として扱う
            print(f"警告: 未知の成長タイプ '{self.growth_type}'。平均型のステータス上昇を適用します。")
            status_gains_dict = get_status_gains_average(self.level)

        hp_increase = status_gains_dict.get("hp", 0) # .get(キー, デフォルト値)で安全に値を取得
        attack_increase = status_gains_dict.get("attack", 0)
        defense_increase = status_gains_dict.get("defense", 0)
            
        self.max_hp += hp_increase
        self.hp = self.max_hp  # レベルアップ時は全回復
        self.attack += attack_increase
        self.defense += defense_increase

        print(f"最大HPが {hp_increase}、攻撃力が {attack_increase}、防御力が {defense_increase} 上昇した！")

        # (スキル習得処理などはそのまま)

        

# 個々のモンスターインスタンスを定義
# (スキルは skills.skills から ALL_SKILLS をインポートして使う形になりますね)
# from skills.skills import ALL_SKILLS # このファイルの先頭でインポート


def show_status(self):
        """モンスターの現在のステータスを表示します。"""
        print(f"名前: {self.name} (Lv.{self.level})")
        if self.element:
            print(f"属性: {self.element}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"攻撃力: {self.attack}")
        print(f"防御力: {self.defense}")
        print(f"経験値: {self.exp}")

        if self.skills:
            print("スキル:")
            for skill_obj in self.skills:
                # Skillオブジェクトに describe() メソッドがあると仮定
                # もし describe() がまだなければ、skill_obj.name などでスキル名を表示
                if hasattr(skill_obj, 'describe') and callable(skill_obj.describe):
                    print(f"  - {skill_obj.describe()}")
                else:
                    print(f"  - {skill_obj.name}") # Skillオブジェクトにname属性があると仮定
        else:
            print("  (スキルなし)")

        if self.status_effects:
            effect_names = ", ".join(self.status_effects)
            print(f"状態異常: {effect_names}")
        # print(f"生存状態: {'生存' if self.is_alive else '戦闘不能'}") # 必要に応じて表示
        print("-" * 20)
# --- 全モンスターを格納する辞書 ---
