# battle.py
import random
from typing import cast
from .player import Player  # Playerクラスは直接使わないが、型ヒントなどで参照される可能性を考慮
from .monsters import Monster  # Monsterクラスのみ参照
from .items.equipment import Equipment, EquipmentInstance, create_titled_equipment
from .skills.skills import Skill  # Skillクラスを参照
from .skills.skill_actions import apply_effects
# import traceback # デバッグ時に必要なら再度有効化

# 属性相性倍率定義
ELEMENTAL_MULTIPLIERS = {
    ("火", "風"): 1.5,
    ("風", "水"): 1.5,
    ("水", "火"): 1.5,
}

# クリティカルヒット設定
CRITICAL_HIT_CHANCE = 0.1
CRITICAL_HIT_MULTIPLIER = 2.0

# --- 状態異常定義 -------------------------------------------------------
def _status_damage(monster: Monster, amount: int):
    monster.hp -= amount
    print(f"{monster.name} は {amount} のダメージを受けた！ (残りHP: {max(0, monster.hp)})")
    if monster.hp <= 0:
        monster.is_alive = False
        print(f"{monster.name} は倒れた！")

def _status_heal(monster: Monster, amount: int):
    if not monster.is_alive:
        return
    before = monster.hp
    monster.hp = min(monster.max_hp, monster.hp + amount)
    healed = monster.hp - before
    if healed:
        print(f"{monster.name} は {healed} 回復した！ (HP: {monster.hp})")

def _slow_apply(monster: Monster):
    monster.apply_buff('speed', -5, 0)
    if monster.speed < 1:
        monster.apply_buff('speed', 1 - monster.speed, 0)

    def revert(m: Monster = monster):
        m.apply_buff('speed', 5, 0)
    return revert

def _charge_apply(monster: Monster):
    monster.apply_buff('defense', -5, 0)
    def revert(m: Monster = monster):
        m.apply_buff('defense', 5, 0)
    return revert

STATUS_DEFINITIONS = {
    "burn": {
        "duration": 3,
        "on_turn": lambda m: _status_damage(m, 3),
        "message": "やけど",
    },
    "poison": {
        "duration": 4,
        "on_turn": lambda m: _status_damage(m, 2),
        "message": "毒",
    },
    "spore_poison": {
        "duration": 3,
        "on_turn": lambda m: _status_damage(m, max(1, m.max_hp // 16)),
        "message": "毒",
    },
    "freeze": {
        "duration": 2,
        "skip_turn": True,
        "message": "こおりつき",
    },
    "paralyze": {
        "duration": 3,
        "skip_chance": 0.5,
        "message": "まひ",
    },
    "regen": {
        "duration": 4,
        "on_turn": lambda m: _status_heal(m, 3),
        "message": "リジェネ",
    },
    "fear": {
        "duration": 2,
        "skip_chance": 0.25,
        "message": "おびえ",
    },
    "blind": {
        "duration": 3,
        "skip_chance": 0.2,
        "message": "盲目",
    },
    "slow": {
        "duration": 3,
        "message": "スロウ",
        "on_apply": lambda m: _slow_apply(m),
    },
    "silence": {
        "duration": 3,
        "message": "サイレンス",
    },
    "curse": {
        "duration": 4,
        "on_turn": lambda m: _status_damage(m, 1),
        "message": "呪い",
    },
    "stun": {
        "duration": 1,
        "skip_turn": True,
        "message": "気絶",
    },
    "sleep": {
        "duration": 3,
        "skip_turn": True,
        "message": "睡眠",
    },
    "confuse": {
        "duration": 3,
        "skip_chance": 0.5,
        "message": "混乱",
    },
    "taunt": {
        "duration": 2,
        "message": "挑発",
    },
    "cant_attack": {
        "duration": 1,
        "message": "攻撃封じ",
    },
    "charging": {
        "duration": 2,
        "message": "チャージ",
        "on_apply": lambda m: _charge_apply(m),
    },
}


def apply_status(target: Monster, status_name: str, duration: int | None = None) -> None:
    data = STATUS_DEFINITIONS.get(status_name)
    if not data:
        print(f"{status_name} の効果は未実装です。")
        return
    dur = duration if duration is not None else data.get("duration", 1)
    entry = {"name": status_name, "remaining": dur}
    on_apply = data.get("on_apply")
    if callable(on_apply):
        try:
            remove_func = on_apply(target)
            if remove_func:
                entry["remove_func"] = remove_func
        except Exception as e:  # noqa: BLE001
            print(f"Error applying status effect {status_name}: {e}")
    target.status_effects.append(entry)
    print(f"{target.name} は{data['message']}状態になった！")


def calculate_damage(attacker: Monster, defender: Monster) -> int:
    """通常攻撃のダメージを計算します。"""
    base = attacker.total_attack() - defender.total_defense()
    damage = max(1, base)

    multiplier = ELEMENTAL_MULTIPLIERS.get((attacker.element, defender.element))
    if multiplier is None:
        # 相手が有利な場合は半減
        rev = ELEMENTAL_MULTIPLIERS.get((defender.element, attacker.element))
        if rev is not None:
            multiplier = 0.5
        else:
            multiplier = 1.0

    damage = int(damage * multiplier)

    # クリティカル判定
    if random.random() < CRITICAL_HIT_CHANCE:
        damage = int(damage * CRITICAL_HIT_MULTIPLIER)

    return max(1, damage)  # 最低1ダメージは保証

def apply_skill_effect(
    caster: Monster,
    targets: list[Monster],
    skill_obj: Skill,
    all_allies: list[Monster] | None = None,
    all_enemies: list[Monster] | None = None,
) -> None:
    """
    スキル効果を対象モンスター(複数可)に適用します。
    caster: スキル使用者
    targets: スキルの主な対象モンスターのリスト
    skill_obj: 使用するスキル
    all_allies: 味方全体のリスト (範囲スキル用)
    all_enemies: 敵全体のリスト (範囲スキル用)
    """
    print(f"\n{caster.name} は {skill_obj.name} を使った！")
    if skill_obj.cost > 0:
        caster.mp = max(0, caster.mp - skill_obj.cost)

    targets_to_use = targets
    if skill_obj.scope == "all":
        if skill_obj.target == "ally" and all_allies is not None:
            targets_to_use = [m for m in all_allies if m.is_alive]
        elif skill_obj.target == "enemy" and all_enemies is not None:
            targets_to_use = [m for m in all_enemies if m.is_alive]

    for target in targets_to_use:  # スキルは複数の対象に影響することがある
        if not target.is_alive:
            print(f"{target.name} は既に倒れているため、{skill_obj.name} の効果を受けなかった。")
            continue

        if skill_obj.effects:
            apply_effects(caster, target, skill_obj.effects, skill_obj)
        else:
            print(f"スキル「{skill_obj.name}」は効果がなかった...")

def display_party_status(party: list[Monster], party_name: str):
    """パーティのステータスを表示します。"""
    print(f"\n--- {party_name} ---")
    for i, monster in enumerate(party):
        status_mark = "💀" if not monster.is_alive else "❤️" # 生存状態マーク
        print(
            f"  {i + 1}. {monster.name} (Lv.{monster.level}, HP: {monster.hp}/{monster.max_hp}, MP: {monster.mp}/{monster.max_mp}) {status_mark}"
        )

def process_status_effects(monster: Monster) -> dict[str, bool]:
    """状態異常を処理し、各種フラグを返す"""
    expired = []
    skip_turn = False
    active_names = [e["name"] for e in monster.status_effects]
    for effect in list(monster.status_effects):
        name = effect["name"]
        data = STATUS_DEFINITIONS.get(name, {})
        on_turn = data.get("on_turn")
        if callable(on_turn):
            on_turn(monster)
            if not monster.is_alive:
                return True
        if data.get("skip_turn"):
            skip_turn = True
        if "skip_chance" in data and random.random() < float(cast(float, data["skip_chance"])):
            skip_turn = True
        effect["remaining"] -= 1
        if effect["remaining"] <= 0:
            remove_cb = effect.get("remove_func")
            if callable(remove_cb):
                try:
                    remove_cb()
                except Exception as e:  # noqa: BLE001
                    print(f"Error removing effect {e} from {monster.name}")
            expired.append(effect)
    for e in expired:
        monster.status_effects.remove(e)
        msg = STATUS_DEFINITIONS.get(e["name"], {}).get("message", e["name"])
        print(f"{monster.name} の {msg} が治った。")
    return {
        "skip_turn": skip_turn,
        "force_attack": "taunt" in active_names,
        "cant_attack": "cant_attack" in active_names,
    }

def process_charge_state(actor: Monster, allies: list[Monster], enemies: list[Monster]) -> bool:
    """Trigger charged skills if the actor is in a charging state."""
    entry = next((e for e in actor.status_effects if e["name"] == "charging"), None)
    if not entry:
        return False
    if entry in actor.status_effects:
        actor.status_effects.remove(entry)
    remove_cb = entry.get("remove_func")
    if callable(remove_cb):
        try:
            remove_cb()
        except Exception as e:  # noqa: BLE001
            print(f"Error removing charge effect from {actor.name}: {e}")
    skill_id = entry.get("release_skill_id")
    if not skill_id:
        return False
    from .skills.skills import ALL_SKILLS  # local import to avoid cycle
    skill_obj = ALL_SKILLS.get(skill_id)
    if skill_obj is None:
        print(f"Unknown release skill id: {skill_id}")
        return False
    targets: list[Monster] = []
    if skill_obj.target == "enemy":
        targets = [m for m in enemies if m.is_alive]
        if skill_obj.scope != "all" and targets:
            targets = [targets[0]]
    elif skill_obj.target == "ally":
        if skill_obj.scope == "all":
            targets = [m for m in allies if m.is_alive]
        else:
            targets = [actor]
    else:
        targets = [actor]
    if targets:
        apply_skill_effect(actor, targets, skill_obj, allies, enemies)
    return True

def get_player_choice(prompt: str, max_choice: int) -> int:
    """プレイヤーに番号で選択させ、有効な値を返すまでループします。"""
    while True:
        try:
            choice_input = input(f"{prompt} (1-{max_choice}, 0でキャンセル/戻る): ")
            choice = int(choice_input)
            if 0 <= choice <= max_choice:
                return choice
            else:
                print(f"1から{max_choice}の間、または0を入力してください。")
        except ValueError:
            print("数字で入力してください。")

def select_target(target_party: list[Monster], prompt: str) -> Monster | None:
    """攻撃/スキル対象を相手パーティから選択させます。生存しているモンスターのみ選択可能。"""
    alive_targets = [m for m in target_party if m.is_alive]
    if not alive_targets:
        print("対象にできるモンスターがいません。")
        return None

    print(prompt)
    for i, monster in enumerate(alive_targets):
        print(f"  {i + 1}. {monster.name} (HP: {monster.hp}/{monster.max_hp})")
    
    choice = get_player_choice("対象を選んでください", len(alive_targets))
    if choice == 0: # キャンセル
        return None
    return alive_targets[choice - 1]

def is_party_defeated(party: list[Monster]) -> bool:
    """パーティが全滅したかどうかを判定します。"""
    return all(not monster.is_alive for monster in party)

def determine_turn_order(party_a: list[Monster], party_b: list[Monster]) -> list[Monster]:
    """Return the action order for this turn sorted by speed."""
    return sorted(
        [m for m in party_a + party_b if m.is_alive],
        key=lambda m: m.total_speed(),
        reverse=True,
    )

def enemy_take_action(enemy_actor: Monster, active_player_party: list[Monster], active_enemy_party: list[Monster]):
    """Execute an enemy monster's turn. Chooses between a normal attack or using a skill."""
    print(f"\n{enemy_actor.name} の行動！")
    alive_player_targets = [m for m in active_player_party if m.is_alive]
    if not alive_player_targets:
        print(f"{enemy_actor.name} は様子を見ている...")
        return

    taunted = any(e["name"] == "taunt" for e in enemy_actor.status_effects)
    cant_attack = any(e["name"] == "cant_attack" for e in enemy_actor.status_effects)

    usable_skills = [s for s in enemy_actor.skills if enemy_actor.mp >= s.cost]

    role = getattr(enemy_actor, "ai_role", "attacker")

    if taunted:
        if cant_attack:
            print(f"{enemy_actor.name} は挑発されているが攻撃できない！")
            return
        if role == "attacker":
            target = min(alive_player_targets, key=lambda m: m.hp)
        else:
            target = random.choice(alive_player_targets)
        print(f"{enemy_actor.name} は挑発により攻撃！ -> {target.name}")
        damage = calculate_damage(enemy_actor, target)
        target.hp -= damage
        print(f"{target.name} は {damage} のダメージを受けた！ (残りHP: {max(0, target.hp)})")
        if target.hp <= 0:
            target.is_alive = False
            print(f"{target.name} は倒れた！")
        return

    selected_skill = None
    skill_targets: list[Monster] = []

    if role == "healer":
        heal_skills = [s for s in usable_skills if s.skill_type == "heal" and s.target == "ally"]
        low_allies = [m for m in active_enemy_party if m.is_alive and m.hp < m.max_hp * 0.5]
        if heal_skills and low_allies:
            ally = min(low_allies, key=lambda m: m.hp / m.max_hp)
            selected_skill = random.choice(heal_skills)
            if selected_skill.scope == "all":
                skill_targets = [m for m in active_enemy_party if m.is_alive]
            else:
                skill_targets = [ally]

    if role == "debuffer" and selected_skill is None:
        debuff_skills = [s for s in usable_skills if s.skill_type == "debuff"]
        if debuff_skills and alive_player_targets:
            target = max(alive_player_targets, key=lambda m: m.attack)
            selected_skill = random.choice(debuff_skills)
            if selected_skill.scope == "all":
                skill_targets = alive_player_targets
            else:
                skill_targets = [target]

    if selected_skill is None and usable_skills and random.random() < 0.5:
        selected_skill = random.choice(usable_skills)
        if selected_skill.target == "enemy":
            if selected_skill.scope == "all":
                skill_targets = alive_player_targets
            else:
                if role == "attacker":
                    target = min(alive_player_targets, key=lambda m: m.hp)
                else:
                    target = random.choice(alive_player_targets)
                skill_targets = [target]
        else:  # ally target
            allies = [m for m in active_enemy_party if m.is_alive]
            if selected_skill.scope == "all":
                skill_targets = allies
            else:
                skill_targets = [random.choice(allies)]

    if selected_skill is not None:
        apply_skill_effect(enemy_actor, skill_targets, selected_skill, active_enemy_party, active_player_party)
    else:
        if cant_attack:
            print(f"{enemy_actor.name} は攻撃できず様子を見ている...")
            return
        if role == "attacker":
            target = min(alive_player_targets, key=lambda m: m.hp)
        else:
            target = random.choice(alive_player_targets)
        print(f"{enemy_actor.name} の攻撃！ -> {target.name}")
        damage = calculate_damage(enemy_actor, target)
        target.hp -= damage
        print(f"{target.name} は {damage} のダメージを受けた！ (残りHP: {max(0, target.hp)})")
        if target.hp <= 0:
            target.is_alive = False
            print(f"{target.name} は倒れた！")

RANK_EXP_MULTIPLIERS = {
    "S": 2.0,
    "A": 1.6,
    "B": 1.3,
    "C": 1.1,
    "D": 1.0,
}

def award_experience(alive_party: list[Monster], defeated_enemies: list[Monster], player: Player | None = None):
    """与えられた敵モンスターリストから総経験値を計算し、味方に分配する"""
    total_exp_reward = 0
    for enemy in defeated_enemies:
        base = (enemy.level * 10) + (enemy.max_hp // 5)
        mult = RANK_EXP_MULTIPLIERS.get(getattr(enemy, "rank", "D"), 1.0)
        total_exp_reward += int(base * mult)
        if player is not None:
            for item_obj, rate in getattr(enemy, "drop_items", []):
                if random.random() < rate:
                    if isinstance(item_obj, Equipment):
                        new_equip = create_titled_equipment(item_obj.equip_id)
                        if new_equip:
                            player.equipment_inventory.append(new_equip)
                            print(f"{new_equip.name} を手に入れた！")
                        else:
                            print(f"{item_obj.name} を手に入れ損ねた...")
                    elif isinstance(item_obj, EquipmentInstance):
                        player.equipment_inventory.append(item_obj)
                        print(f"{item_obj.name} を手に入れた！")
                    else:
                        player.items.append(item_obj)
                        print(f"{item_obj.name} を手に入れた！")

    alive_monsters = [m for m in alive_party if m.is_alive]
    if alive_monsters and total_exp_reward > 0:
        base_share = total_exp_reward // len(alive_monsters)
        remainder = total_exp_reward % len(alive_monsters)
        print("\n--- 経験値獲得 ---")
        for idx, monster in enumerate(alive_monsters):
            share = base_share + (1 if idx < remainder else 0)
            if share > 0:
                monster.gain_exp(share)
    else:
        print("獲得経験値はありませんでした。")

def attempt_scout(player: Player | None, target: Monster, enemy_party: list[Monster]) -> bool:
    """敵モンスターをスカウトして仲間にする試みを行う。成功するとTrueを返す。"""
    if target is None or not target.is_alive:
        print("対象がいません。")
        return False

    rate = getattr(target, "scout_rate", 0.25)
    print(f"\n{target.name} をスカウトしている...")

    if random.random() < rate:
        print(f"{target.name} は仲間になりたそうにこちらを見ている！")
        if player is not None:
            player.add_monster_to_party(target)
        target.is_alive = False
        if target in enemy_party:
            enemy_party.remove(target)
        return True
    else:
        print(f"{target.name} は警戒している。仲間にならなかった。")
        return False

