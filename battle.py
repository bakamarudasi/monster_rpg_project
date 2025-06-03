# battle.py
import random
from player import Player # Playerクラスは直接使わないが、型ヒントなどで参照される可能性を考慮
from monsters import Monster, ALL_MONSTERS # MonsterクラスとALL_MONSTERSを参照
from skills.skills import Skill # Skillクラスを参照
# import traceback # デバッグ時に必要なら再度有効化

def calculate_damage(attacker: Monster, defender: Monster) -> int:
    """通常攻撃のダメージを計算します。"""
    # TODO: 属性相性やクリティカルヒットなどの要素を追加する
    damage = attacker.attack - defender.defense
    return max(1, damage) # 最低1ダメージは保証

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

    for target in targets: # スキルは複数の対象に影響することがある
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
            if skill_obj.target == "ally": # 現状は単体対象を想定
                original_hp = target.hp
                target.hp += skill_obj.power
                target.hp = min(target.hp, target.max_hp)
                healed_amount = target.hp - original_hp
                print(f"{target.name} のHPが {healed_amount} 回復した！ (現在HP: {target.hp})")
            # TODO: 味方全体回復 (all_allies を使う) もここに追加

        elif skill_obj.skill_type == "buff":
            if skill_obj.target == "ally" and callable(skill_obj.effect):
                try:
                    skill_obj.effect(target) # Monsterオブジェクト(スキル対象)を渡す
                    print(f"{target.name} の何かが強化された！")
                except Exception as e:
                    print(f"スキル効果の適用中にエラー: {e}")
            # TODO: 味方全体バフも
        else:
            print(f"スキル「{skill_obj.name}」は効果がなかった...") # 未対応のスキルタイプなど

def display_party_status(party: list[Monster], party_name: str):
    """パーティのステータスを表示します。"""
    print(f"\n--- {party_name} ---")
    for i, monster in enumerate(party):
        status_mark = "💀" if not monster.is_alive else "❤️" # 生存状態マーク
        print(f"  {i + 1}. {monster.name} (Lv.{monster.level}, HP: {monster.hp}/{monster.max_hp}) {status_mark}")

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

        # --- プレイヤーのターン ---
        print("\n>>> プレイヤーのターン <<<")
        display_party_status(active_player_party, "味方パーティ")
        display_party_status(active_enemy_party, "敵パーティ")

        # 行動するモンスターを選択 (生存しているモンスターのみ)
        print("\n行動するモンスターを選んでください:")
        alive_player_monsters = [m for m in active_player_party if m.is_alive]
        if not alive_player_monsters: # 万が一、ターン開始時に行動できる味方がいなければ敗北
            break 
        
        for i, monster in enumerate(alive_player_monsters):
            print(f"  {i + 1}. {monster.name}")
        
        actor_choice = get_player_choice("選択", len(alive_player_monsters))
        if actor_choice == 0: # ターンをスキップするような処理は現状なし (将来的に「防御」などを追加するなら考慮)
            print("行動モンスターの選択をキャンセルしました。") # 実際にはありえないが、get_player_choiceが0を返す場合
            continue

        player_actor = alive_player_monsters[actor_choice - 1]
        print(f"\n{player_actor.name} の行動！")

        # 行動選択
        print("1: たたかう")
        print("2: スキル")
        print("3: にげる")
        # TODO: 4: アイテム, 5: 交代 などを追加

        action_choice = get_player_choice("行動を選んでください", 3)

        if action_choice == 1: # たたかう
            target = select_target(active_enemy_party, "\n攻撃対象を選んでください:")
            if target:
                print(f"\n{player_actor.name} の攻撃！ -> {target.name}")
                damage = calculate_damage(player_actor, target)
                target.hp -= damage
                print(f"{target.name} に {damage} のダメージを与えた！ (残りHP: {max(0, target.hp)})")
                if target.hp <= 0:
                    target.is_alive = False
                    print(f"{target.name} を倒した！")
            else:
                print("攻撃をキャンセルしました。")
                continue # 行動選択に戻る (またはターン終了)

        elif action_choice == 2: # スキル
            if not player_actor.skills:
                print(f"{player_actor.name} は覚えているスキルがない！")
                continue

            print("\nどのスキルを使いますか？")
            for i, skill in enumerate(player_actor.skills):
                print(f"  {i + 1}: {skill.describe()}")
            
            skill_choice_idx = get_player_choice("スキル番号を選んでください", len(player_actor.skills))
            if skill_choice_idx == 0:
                print("スキル使用をキャンセルしました。")
                continue
            
            selected_skill = player_actor.skills[skill_choice_idx - 1]
            
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
                # 現状は使用者自身を対象とする
                skill_targets.append(player_actor)
            # TODO: 他のスキルタイプやターゲット指定（敵全体、味方全体など）の処理
            
            if skill_targets:
                apply_skill_effect(player_actor, skill_targets, selected_skill, active_player_party, active_enemy_party)
            else:
                print(f"{selected_skill.name} は適切な対象に使えなかった。")
                continue
        
        elif action_choice == 3: # にげる
            print(f"\n{player_actor.name} は逃げ出そうとした！")
            if random.random() < 0.5: # 50%の確率で成功
                print("うまく逃げ切れた！")
                fled = True
            else:
                print("しかし、回り込まれてしまった！")
        
        else: # action_choice == 0 (キャンセル)
            print("行動をキャンセルしました。")
            continue

        # プレイヤーの行動後、敵パーティが全滅したかチェック
        if is_party_defeated(active_enemy_party):
            break
        if fled: # 逃走成功なら戦闘終了
            break

        # --- 敵のターン ---
        print("\n>>> 敵のターン <<<")
        for enemy_actor in active_enemy_party:
            if not enemy_actor.is_alive: # 既に倒れていればスキップ
                continue
            if is_party_defeated(active_player_party): # プレイヤー側が全滅していれば敵のターンは終了
                break

            print(f"\n{enemy_actor.name} の行動！")
            # 敵の行動AI (現状はランダムな生存プレイヤーモンスターに通常攻撃)
            alive_player_targets = [m for m in active_player_party if m.is_alive]
            if not alive_player_targets: # 万が一、攻撃対象がいなければ何もしない
                print(f"{enemy_actor.name} は様子を見ている...")
                continue

            target = random.choice(alive_player_targets)
            print(f"{enemy_actor.name} の攻撃！ -> {target.name}")
            damage = calculate_damage(enemy_actor, target)
            target.hp -= damage
            print(f"{target.name} は {damage} のダメージを受けた！ (残りHP: {max(0, target.hp)})")
            if target.hp <= 0:
                target.is_alive = False
                print(f"{target.name} は倒れた！")
        
        # 敵の行動後、プレイヤーパーティが全滅したかチェック
        if is_party_defeated(active_player_party):
            break

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
        
        # 勝利時の経験値獲得処理 (生存している味方モンスターに分配)
        # TODO: より詳細な経験値計算ロジック
        total_exp_reward = 0
        for defeated_enemy in enemy_party:  # 元のenemy_partyを参照して倒した敵の情報を得る
            if not defeated_enemy.is_alive:  # この戦闘で倒された敵
                total_exp_reward += (defeated_enemy.level * 10) + (defeated_enemy.max_hp // 5)
                if player is not None:
                    for item_obj, rate in getattr(defeated_enemy, "drop_items", []):
                        if random.random() < rate:
                            player.items.append(item_obj)
                            print(f"{item_obj.name} を手に入れた！")
        
        alive_player_monsters_after_battle = [m for m in active_player_party if m.is_alive]
        if alive_player_monsters_after_battle and total_exp_reward > 0:
            exp_per_monster = total_exp_reward // len(alive_player_monsters_after_battle)
            if exp_per_monster > 0:
                print(f"\n--- 経験値獲得 ---")
                for monster in alive_player_monsters_after_battle:
                    # player_party内の元のモンスターインスタンスに経験値を与える
                    # active_player_party のモンスターは player_party の要素への参照なので、直接変更が反映される
                    monster.gain_exp(exp_per_monster)
            else:
                print("獲得経験値はありませんでした。")

    else:
        print("戦いは決着がつかなかったようだ...") # 引き分けなど特殊なケース
        battle_result = "draw" # 未定義だが、将来的な拡張用

    # main.py には戦闘結果の文字列だけを返すように変更。
    # モンスターオブジェクトの更新は、active_player_party (これはplayer_partyの要素への参照) への変更を通じて
    # 呼び出し元の player_party に直接反映される。
    return battle_result
