# battle.py (スキルコマンド機能を追加)
from player import Player 
#
from monsters import Monster, ALL_MONSTERS 
from skills.skills import Skill 

def calculate_damage(attacker, defender):
    # 通常攻撃のダメージ計算 (仮)
    damage = attacker.attack - defender.defense
    return max(1, damage)

def apply_skill_effect(caster, target, skill_obj, all_allies=None, all_enemies=None):
    """スキル効果を適用する関数 (簡易版)
    caster: スキル使用者 (Monsterオブジェクト)
    target: 主な対象 (Monsterオブジェクト)
    skill_obj: 使用するスキル (Skillオブジェクト)
    all_allies: 味方全体のリスト (範囲スキル用)
    all_enemies: 敵全体のリスト (範囲スキル用)
    """
    print(f"\n{caster.name} は {skill_obj.name} を使った！")

    if skill_obj.skill_type == "attack":
        # 攻撃スキルの場合 (例: スキルのpowerを基本ダメージとし、防御力で軽減)
        # より複雑な計算式も可能です (例: caster.attack + skill_obj.power - target.defense)
        damage = skill_obj.power 
        actual_damage = max(1, damage - target.defense) # 防御力を考慮
        target.hp -= actual_damage
        print(f"{target.name} に {actual_damage} のダメージ！ (残りHP: {max(0, target.hp)})")
        if target.hp <= 0:
            target.is_alive = False # HPが0以下なら戦闘不能に
            # print(f"{target.name} を倒した！") # メッセージは呼び出し元で出す方が良いかも

    elif skill_obj.skill_type == "heal":
        if skill_obj.target == "ally": # 対象が味方単体の場合
            original_hp = caster.hp
            caster.hp += skill_obj.power
            caster.hp = min(caster.hp, caster.max_hp) # 最大HPを超えない
            healed_amount = caster.hp - original_hp
            print(f"{caster.name} のHPが {healed_amount} 回復した！ (現在HP: {caster.hp})")
        # TODO: 将来的には味方全体回復 (all_allies を使う) もここに追加

    elif skill_obj.skill_type == "buff":
        if skill_obj.target == "ally" and callable(skill_obj.effect):
            try:
                skill_obj.effect(caster) # Monsterオブジェクトを渡す
                # 効果の具体的なメッセージは effect 関数内か、ここで補足
                print(f"{caster.name} の何かが強化された！") 
            except Exception as e:
                print(f"スキル効果の適用中にエラー: {e}")
        # TODO: 将来的には味方全体バフも

    # elif skill_obj.skill_type == "debuff":
    # TODO: デバフ処理 (敵対象)
    
    # elif skill_obj.skill_type == "status":
    # TODO: 状態異常を付与する処理

    else:
        print("しかし、特に何も起こらなかった...")


def start_battle(player_monster, enemy_monster): # 将来的には player_party を受け取る
    print(f"\n--- 戦闘開始！ ---")
    print(f"{player_monster.name} (HP: {player_monster.hp}) VS {enemy_monster.name} (HP: {enemy_monster.hp})")

    turn = 1
    battle_over = False

    while player_monster.is_alive and enemy_monster.is_alive and not battle_over:
        print(f"\n----- ターン {turn} -----")
        print(f"{player_monster.name} HP: {player_monster.hp} | {enemy_monster.name} HP: {enemy_monster.hp}")

        # --- プレイヤーのターン ---
        print(f"\nどうする？ ({player_monster.name} のターン)")
        action = input("コマンドを選んでください (1:たたかう, 2:スキル, 3:にげる): ") # スキルを追加

        if action == "1":  # たたかう
            print(f"\n{player_monster.name} の攻撃！")
            damage_to_enemy = calculate_damage(player_monster, enemy_monster)
            enemy_monster.hp -= damage_to_enemy
            print(f"{enemy_monster.name} に {damage_to_enemy} のダメージを与えた！")
            print(f"{enemy_monster.name} の残りHP: {max(0, enemy_monster.hp)}")
            if enemy_monster.hp <= 0:
                enemy_monster.is_alive = False
                print(f"\n{enemy_monster.name} を倒した！")

        elif action == "2":  # スキル
            if not player_monster.skills: # スキルを覚えていなかったら
                print("覚えているスキルがない！")
                continue # ターンやり直し

            print("\nどのスキルを使いますか？")
            for i, skill in enumerate(player_monster.skills):
                # Skillオブジェクトに describe メソッドがあると仮定
                print(f"  {i + 1}: {skill.describe()}") 
            
            skill_choice_input = input(f"スキル番号を選んでください (1-{len(player_monster.skills)}, 0:キャンセル): ")

            if not skill_choice_input.isdigit(): # 数字以外の入力は無効
                print("無効な入力です。数字で選んでください。")
                continue

            skill_choice = int(skill_choice_input)

            if skill_choice == 0: # キャンセル選択
                print("スキル使用をキャンセルしました。")
                continue # ターンやり直し (コマンド選択から)
            elif 1 <= skill_choice <= len(player_monster.skills):
                selected_skill = player_monster.skills[skill_choice - 1] # 選択されたSkillオブジェクト
                
                # ターゲットを決定 (現状は攻撃なら敵、それ以外なら使用者自身)
                target_for_skill = None
                if selected_skill.skill_type == "attack":
                    target_for_skill = enemy_monster
                elif selected_skill.skill_type in ["heal", "buff"] and selected_skill.target == "ally":
                    target_for_skill = player_monster
                # TODO: 他のターゲット指定 ("all_enemies", "all_allies" など) の処理

                if target_for_skill:
                    apply_skill_effect(player_monster, target_for_skill, selected_skill)
                    if not target_for_skill.is_alive: # スキルで敵を倒した場合など
                         print(f"\n{target_for_skill.name} を倒した！") # apply_skill_effect内でis_aliveは更新される
                else:
                    print(f"{selected_skill.name} は今は適切な対象に使えないようだ。")
                    continue # ターンやり直し
            else:
                print("無効なスキル番号です。")
                continue # ターンやり直し
        
        elif action == "3":  # にげる
            print(f"\n{player_monster.name} は逃げ出そうとした！")
            print("うまく逃げ切れた！") # 今回は必ず成功
            battle_over = True
        
        else:
            print("そのコマンドは存在しません。もう一度入力してください。")
            continue

        if not enemy_monster.is_alive or battle_over:
            break

        # --- 敵のターン ---
        # (変更なし、現状は毎回たたかうのみ)
        print(f"\n{enemy_monster.name} の攻撃！")
        damage_to_player = calculate_damage(enemy_monster, player_monster)
        player_monster.hp -= damage_to_player
        print(f"{player_monster.name} は {damage_to_player} のダメージを受けた！")
        print(f"{player_monster.name} の残りHP: {max(0, player_monster.hp)}")
        if player_monster.hp <= 0:
            player_monster.is_alive = False
            print(f"\n{player_monster.name} は倒れてしまった...")
        
        if battle_over: # プレイヤーが逃げた場合など
             break

        turn += 1
    
    # --- 戦闘終了後の処理 ---
    # (変更なし)
    print("\n----- 戦闘終了 -----")
    if battle_over and action == "3": # 逃げた場合 (コマンド番号が3になったので修正)
        print(f"{player_monster.name} は戦闘から離脱した。")
    elif player_monster.is_alive and not enemy_monster.is_alive: # プレイヤーの勝利
        print(f"{player_monster.name} は戦いに勝利した！")
        
        # 経験値の計算 (例: 倒した敵のレベル * 15 + 敵の基本HPの1/10)
        exp_reward = (enemy_monster.level * 15) + (enemy_monster.max_hp // 10)
        # print(f"{enemy_monster.name} を倒して、経験値を獲得するチャンス！") # メッセージ調整
        
        # 戦闘に参加したモンスターに経験値を与える
        player_monster.gain_exp(exp_reward) # player_monster は戦闘に参加したモンスター
        
        # 将来的にパーティメンバー複数で戦うようになったら、
        # 経験値を分配したり、全員が獲得したりする処理をここに書きます。
        
        # (アイテムドロップなどの処理もここに追加できます)

    elif not player_monster.is_alive: # プレイヤーの敗北
        print(f"{player_monster.name} のパーティは全滅した...")
        # ゲームオーバー処理など
    else: # その他の場合
        print("戦いは終わった。")