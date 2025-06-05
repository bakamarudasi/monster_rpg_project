# battle.py
import random
from player import Player  # Playerクラスは直接使わないが、型ヒントなどで参照される可能性を考慮
from monsters import Monster, ALL_MONSTERS  # MonsterクラスとALL_MONSTERSを参照
from skills.skills import Skill  # Skillクラスを参照
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

def calculate_damage(attacker: Monster, defender: Monster) -> int:
    """通常攻撃のダメージを計算します。"""
    base = attacker.attack - defender.defense
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

def apply_skill_effect(caster: Monster, targets: list[Monster], skill_obj: Skill, all_allies: list[Monster] = None, all_enemies: list[Monster] = None):
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
        if not target.is_alive: # 対象が既に倒れていたらスキップ
            print(f"{target.name} は既に倒れているため、{skill_obj.name} の効果を受けなかった。")
            continue

        if skill_obj.skill_type == "attack":
            damage = skill_obj.power
            actual_damage = max(1, damage - target.defense)
            target.hp -= actual_damage
            print(f"{target.name} に {actual_damage} のダメージ！ (残りHP: {max(0, target.hp)})")
            if target.hp <= 0:
                target.is_alive = False
                print(f"{target.name} は倒れた！")

        elif skill_obj.skill_type == "heal":
            if skill_obj.target == "ally":
                original_hp = target.hp
                target.hp += skill_obj.power
                target.hp = min(target.hp, target.max_hp)
                healed_amount = target.hp - original_hp
                print(f"{target.name} のHPが {healed_amount} 回復した！ (現在HP: {target.hp})")

        elif skill_obj.skill_type == "buff":
            if skill_obj.target == "ally":
                # effect が関数ならそれを実行、文字列の場合は簡易的なバフを実装
                if callable(skill_obj.effect):
                    try:
                        remove_func = skill_obj.effect(target)
                        if skill_obj.duration > 0:
                            target.status_effects.append({
                                "name": skill_obj.name,
                                "remaining": skill_obj.duration,
                                "remove_func": remove_func,
                            })
                        print(f"{target.name} の何かが強化された！")
                    except Exception as e:
                        print(f"スキル効果の適用中にエラー: {e}")
                elif isinstance(skill_obj.effect, str):
                    try:
                        if skill_obj.effect == "speed_up":
                            amount = 5
                            target.speed += amount
                            def revert(m=target, a=amount):
                                m.speed -= a
                        elif skill_obj.effect == "atk_def_up":
                            amount = 5
                            target.attack += amount
                            target.defense += amount
                            def revert(m=target, a=amount):
                                m.attack -= a
                                m.defense -= a
                        else:
                            print(f"{skill_obj.effect} の効果は未実装です。")
                            continue
                        if skill_obj.duration > 0:
                            target.status_effects.append({
                                "name": skill_obj.name,
                                "remaining": skill_obj.duration,
                                "remove_func": revert,
                            })
                        print(f"{target.name} の能力が上がった！")
                    except Exception as e:
                        print(f"スキル効果の適用中にエラー: {e}")
            
        else:
            print(f"スキル「{skill_obj.name}」は効果がなかった...") # 未対応のスキルタイプなど

def display_party_status(party: list[Monster], party_name: str):
    """パーティのステータスを表示します。"""
    print(f"\n--- {party_name} ---")
    for i, monster in enumerate(party):
        status_mark = "💀" if not monster.is_alive else "❤️" # 生存状態マーク
        print(
            f"  {i + 1}. {monster.name} (Lv.{monster.level}, HP: {monster.hp}/{monster.max_hp}, MP: {monster.mp}/{monster.max_mp}) {status_mark}"
        )

def process_status_effects(monster: Monster):
    expired = []
    for effect in monster.status_effects:
        effect["remaining"] -= 1
        if effect["remaining"] <= 0:
            if callable(effect.get("remove_func")):
                try:
                    effect["remove_func"]()
                except Exception:
                    pass
            expired.append(effect)
    for e in expired:
        monster.status_effects.remove(e)
        print(f"{monster.name} の {e['name']} の効果が切れた。")

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
        key=lambda m: m.speed,
        reverse=True,
    )

def enemy_take_action(enemy_actor: Monster, active_player_party: list[Monster], active_enemy_party: list[Monster]):
    """Execute an enemy monster's turn. Chooses between a normal attack or using a skill."""
    print(f"\n{enemy_actor.name} の行動！")
    alive_player_targets = [m for m in active_player_party if m.is_alive]
    if not alive_player_targets:
        print(f"{enemy_actor.name} は様子を見ている...")
        return

    usable_skills = [s for s in enemy_actor.skills if enemy_actor.mp >= s.cost]
    if usable_skills and random.random() < 0.5:
        selected_skill = random.choice(usable_skills)
        if selected_skill.target == "enemy":
            if selected_skill.scope == "all":
                skill_targets = alive_player_targets
            else:
                skill_targets = [random.choice(alive_player_targets)]
        else:  # ally target
            allies = [m for m in active_enemy_party if m.is_alive]
            if selected_skill.scope == "all":
                skill_targets = allies
            else:
                skill_targets = [random.choice(allies)]

        apply_skill_effect(enemy_actor, skill_targets, selected_skill, active_enemy_party, active_player_party)
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

def attempt_scout(player: Player, target: Monster, enemy_party: list[Monster]) -> bool:
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

def start_battle(player_party: list[Monster], enemy_party: list[Monster], player: Player | None = None):
    """
    3vs3の戦闘を開始します。
    player_party: プレイヤーのモンスターパーティ (最大3体想定)
    enemy_party: 敵のモンスターパーティ (1体～3体想定)
    player: 戦闘結果の報酬を受け取るプレイヤー
    戻り値: (戦闘結果フラグ: "win", "lose", "fled")
    """
    print("\n!!! バトル開始 !!!")
    
    # 戦闘に参加するモンスターを最大3体に制限 (先頭から)
    active_player_party = [m for m in player_party if m.is_alive][:3]
    active_enemy_party = [m for m in enemy_party if m.is_alive][:3]

    if player is not None and hasattr(player, "monster_book"):
        for e in enemy_party:
            player.monster_book.register_seen(e.monster_id)

    if not active_player_party:
        print("戦えるモンスターがプレイヤー側にいません！")
        return "lose" # 即時敗北

    print("\n--- 味方パーティ ---")
    for m in active_player_party:
        print(f"{m.name} (HP: {m.hp}/{m.max_hp})")
    print("\n--- 敵パーティ ---")
    for m in active_enemy_party:
        print(f"{m.name} (HP: {m.hp}/{m.max_hp})")

    turn = 1
    fled = False

    while not is_party_defeated(active_player_party) and not is_party_defeated(active_enemy_party) and not fled:
        print(f"\n\n--- ターン {turn} ---")

        display_party_status(active_player_party, "味方パーティ")
        display_party_status(active_enemy_party, "敵パーティ")

        # このターンに行動する順序を速度順で決める
        turn_order = determine_turn_order(active_player_party, active_enemy_party)

        for actor in turn_order:
            if fled:
                break
            if is_party_defeated(active_player_party) or is_party_defeated(active_enemy_party):
                break
            if not actor.is_alive:
                continue

            process_status_effects(actor)

            if actor in active_player_party:
                while True:
                    print(f"\n>>> {actor.name} の行動！ <<<")
                    print("1: たたかう")
                    print("2: スキル")
                    print("3: アイテム")
                    print("4: スカウト")
                    print("5: にげる")
                    action_choice = get_player_choice("行動を選んでください", 5)

                    if action_choice == 1:  # たたかう
                        target = select_target(active_enemy_party, "\n攻撃対象を選んでください:")
                        if target:
                            print(f"\n{actor.name} の攻撃！ -> {target.name}")
                            damage = calculate_damage(actor, target)
                            target.hp -= damage
                            print(f"{target.name} に {damage} のダメージを与えた！ (残りHP: {max(0, target.hp)})")
                            if target.hp <= 0:
                                target.is_alive = False
                                print(f"{target.name} を倒した！")
                            break
                        else:
                            print("攻撃をキャンセルしました。")
                            continue

                    elif action_choice == 2:  # スキル
                        if not actor.skills:
                            print(f"{actor.name} は覚えているスキルがない！")
                            continue

                        print("\nどのスキルを使いますか？")
                        for i, skill in enumerate(actor.skills):
                            print(f"  {i + 1}: {skill.describe()}")

                        skill_choice_idx = get_player_choice("スキル番号を選んでください", len(actor.skills))
                        if skill_choice_idx == 0:
                            print("スキル使用をキャンセルしました。")
                            continue

                        selected_skill = actor.skills[skill_choice_idx - 1]

                        if actor.mp < selected_skill.cost:
                            print(f"MPが足りない！ {selected_skill.name} を使えない。")
                            continue

                        # スキルの対象を選択
                        skill_targets = []
                        if selected_skill.skill_type == "attack":
                            target_monster = select_target(active_enemy_party, f"\n{selected_skill.name} の対象を選んでください:")
                            if target_monster:
                                skill_targets.append(target_monster)
                            else:
                                print("スキル対象の選択をキャンセルしました。")
                                continue
                        elif selected_skill.skill_type == "heal" and selected_skill.target == "ally":
                            if selected_skill.scope == "all":
                                skill_targets = [m for m in active_player_party if m.is_alive]
                            else:
                                target_monster = select_target(active_player_party, f"\n{selected_skill.name} の回復対象を選んでください:")
                                if target_monster:
                                    skill_targets.append(target_monster)
                                else:
                                    print("スキル対象の選択をキャンセルしました。")
                                    continue

                        if skill_targets:
                            apply_skill_effect(actor, skill_targets, selected_skill, active_player_party, active_enemy_party)
                            break
                        else:
                            print(f"{selected_skill.name} は適切な対象に使えなかった。")
                            continue

                    elif action_choice == 3:  # アイテム
                        if player is None:
                            print("アイテムを使うプレイヤーがいない。")
                            continue
                        if not player.items:
                            print("アイテムを持っていない。")
                            continue
                        player.show_items()
                        item_choice = get_player_choice("使うアイテム番号を選んでください", len(player.items))
                        if item_choice == 0:
                            print("アイテム使用をキャンセルしました。")
                            continue
                        target_monster = select_target(active_player_party, "\n回復対象を選んでください:")
                        if target_monster is None:
                            print("アイテム使用をキャンセルしました。")
                            continue
                        used = player.use_item(item_choice - 1, target_monster)
                        if used:
                            break
                        else:
                            continue

                    elif action_choice == 4:  # スカウト
                        target = select_target(active_enemy_party, "\nスカウトする対象を選んでください:")
                        if target:
                            attempt_scout(player, target, enemy_party)
                            if not target.is_alive and target in active_enemy_party:
                                active_enemy_party.remove(target)
                            break
                        else:
                            print("スカウトをキャンセルしました。")
                            continue

                    elif action_choice == 5:  # にげる
                        print(f"\n{actor.name} は逃げ出そうとした！")
                        if random.random() < 0.5:
                            print("うまく逃げ切れた！")
                            fled = True
                            break
                        else:
                            print("しかし、回り込まれてしまった！")
                            break

                    else:  # action_choice == 0 (キャンセル)
                        print("行動をキャンセルしました。")
                        continue

            else:  # 敵モンスターの行動
                enemy_actor = actor
                if not enemy_actor.is_alive:
                    continue
                if is_party_defeated(active_player_party):
                    break

                enemy_take_action(enemy_actor, active_player_party, active_enemy_party)

        turn += 1

    # --- 戦闘終了後の処理 ---
    print("\n\n戦闘終了！")
    battle_result = ""
    if fled:
        print("戦闘から逃げ出した。")
        battle_result = "fled"
    elif is_party_defeated(active_player_party):
        print("味方パーティは全滅した...")
        battle_result = "lose"
    elif is_party_defeated(active_enemy_party):
        print("敵パーティを全て倒した！味方の勝利！")
        battle_result = "win"
        
        # 勝利時の経験値獲得処理
        defeated = [e for e in enemy_party if not e.is_alive]
        award_experience(active_player_party, defeated, player)

    else:
        print("戦いは決着がつかなかったようだ...") # 引き分けなど特殊なケース
        battle_result = "draw" # 未定義だが、将来的な拡張用

    # main.py には戦闘結果の文字列だけを返すように変更。
    # モンスターオブジェクトの更新は、active_player_party (これはplayer_partyの要素への参照) への変更を通じて
    # 呼び出し元の player_party に直接反映される。
    return battle_result
