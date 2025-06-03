from skills.skills import ALL_SKILLS
import copy # deepcopyのためにインポート

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
    try:
        hp_gain = 5 + (current_level // 5)
        attack_gain = 2 + (current_level // 10)
        defense_gain = 2 + (current_level // 10)
        return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}
    except Exception as e:
        raise 

def get_status_gains_early(current_level):
    try:
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
        return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}
    except Exception as e:
        raise

def get_status_gains_late(current_level):
    try:
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
        return {"hp": hp_gain, "attack": attack_gain, "defense": defense_gain}
    except Exception as e:
        raise

def calculate_exp_for_average(current_level):
    try:
        return (current_level ** 2) * 20 + 50
    except Exception as e:
        raise

def calculate_exp_for_early(current_level):
    try:
        if current_level < 10:
            return (current_level ** 2) * 15 + 30
        elif current_level < 30:
            return (current_level ** 2) * 25 + 100
        else:
            return (current_level ** 3) * 10 + 500
    except Exception as e:
        raise

def calculate_exp_for_late(current_level):
    try:
        if current_level < 15:
            return (current_level ** 2) * 30 + 100
        else:
            return (current_level ** 2) * 20 + 50
    except Exception as e:
        raise

class Monster:
    def __init__(self, name, hp, attack, defense, level=1, exp=0, element=None, skills=None, 
                 growth_type=GROWTH_TYPE_AVERAGE, monster_id=None, image_filename=None, rank=RANK_D): # rank 引数を追加 (デフォルトDランク)
        self.name = name
        self.hp = hp
        self.max_hp = hp
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
        self.rank = rank # rank 属性を保存

    def show_status(self):
        print(f"名前: {self.name} (ID: {self.monster_id}, Lv.{self.level}, Rank: {self.rank})") # ランクも表示
        if self.element:
            print(f"属性: {self.element}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"攻撃力: {self.attack}")
        print(f"防御力: {self.defense}")
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
            effect_names = ", ".join(self.status_effects)
            print(f"状態異常: {effect_names}")
        print("-" * 20)

    def calculate_exp_to_next_level(self):
        try:
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
        except Exception as e:
            raise 

    def gain_exp(self, amount):
        try:
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
        except Exception as e:
            raise 

    def level_up(self):
        try:
            self.level += 1
            print(f"🎉🎉🎉 {self.name} は レベル {self.level} に上がった！ 🎉🎉🎉")

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
                status_gains_dict = {"hp": 1, "attack": 1, "defense": 1} 

            hp_increase = status_gains_dict.get("hp", 0)
            attack_increase = status_gains_dict.get("attack", 0)
            defense_increase = status_gains_dict.get("defense", 0)
                
            self.max_hp += hp_increase
            self.hp = self.max_hp 
            self.attack += attack_increase
            self.defense += defense_increase

            print(f"最大HPが {hp_increase}、攻撃力が {attack_increase}、防御力が {defense_increase} 上昇した！")
        except Exception as e:
            raise 

    def copy(self):
        try:
            new_skills = [copy.deepcopy(skill) for skill in self.skills]
            
            new_monster = Monster(
                name=self.name,
                hp=self.max_hp, 
                attack=self.attack,
                defense=self.defense,
                level=self.level, 
                exp=self.exp,    
                element=self.element,
                skills=new_skills,
                growth_type=self.growth_type,
                monster_id=self.monster_id, 
                image_filename=self.image_filename,
                rank=self.rank # rank 属性をコピー時に引き継ぐ
            )
            new_monster.max_hp = self.max_hp 
            new_monster.hp = new_monster.max_hp 
            new_monster.is_alive = True 
            return new_monster
        except Exception as e:
            raise 
