# battle.py
import random # 逃走成功判定のためインポート
from player import Player 
from monsters import Monster, ALL_MONSTERS 
from skills.skills import Skill 
# import traceback # traceback.print_exc() を使わない場合は不要

def calculate_damage(attacker, defender):
    # 通常攻撃のダメージ計算 (仮)
    # TODO: 属性相性やクリティカルヒットなどの要素を追加する
    damage = attacker.attack - defender.defense
    return max(1, damage) # 最低1ダメージは保証

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
        # 攻撃スキルの場合
        damage = skill_obj.power 
        actual_damage = max(1, damage - target.defense) # 防御力を考慮
        target.hp -= actual_damage
        print(f"{target.name} に {actual_damage} のダメージ！ (残りHP: {max(0, target.hp)})")
        if target.hp <= 0:
            target.is_alive = False # HPが0以下なら戦闘不能に

    elif skill_obj.skill_type == "heal":
        if skill_obj.target == "ally": 
            original_hp = target.hp 
            target.hp += skill_obj.power
            target.hp = min(target.hp, target.max_hp) 
            healed_amount = target.hp - original_hp
            print(f"{target.name} のHPが {healed_amount} 回復した！ (現在HP: {target.hp})")

    elif skill_obj.skill_type == "buff":
        if skill_obj.target == "ally" and callable(skill_obj.effect): 
            try:
                skill_obj.effect(target) 
                print(f"{target.name} の何かが強化された！") 
            except Exception as e:
                print(f"スキル効果の適用中にエラー: {e}")
    else:
        print("しかし、特に何も起こらなかった...")


def start_battle(player_monster: Monster, enemy_monster: Monster): # 型ヒントを追加
    """
    プレイヤーモンスターと敵モンスターの戦闘を開始します。
    戦闘終了後、更新されたプレイヤーモンスター、敵モンスター、および逃走フラグを返します。
    """
    print(f"\n--- 戦闘開始！ ---")
    print(f"{player_monster.name} (HP: {player_monster.hp}) VS {enemy_monster.name} (HP: {enemy_monster.hp})")

    turn = 1
    fled = False # プレイヤーが逃走したかどうかのフラグ

    if not player_monster.is_alive or player_monster.hp <= 0:
        print(f"{player_monster.name} は戦える状態ではありません。戦闘を開始できません。")
        player_monster.is_alive = False 
        # print(f"[DEBUG battle.py] Early return from start_battle (player not alive)")
        return player_monster, enemy_monster, True 

    if not enemy_monster.is_alive or enemy_monster.hp <= 0:
        print(f"{enemy_monster.name} は既に倒れています。戦闘を開始できません。")
        enemy_monster.is_alive = False 
        # print(f"[DEBUG battle.py] Early return from start_battle (enemy not alive)")
        return player_monster, enemy_monster, False 


    while player_monster.is_alive and enemy_monster.is_alive and not fled:
        print(f"\n----- ターン {turn} -----")
        print(f"{player_monster.name} HP: {player_monster.hp} | {enemy_monster.name} HP: {enemy_monster.hp}")

        print(f"\nどうする？ ({player_monster.name} のターン)")
        action = input("コマンドを選んでください (1:たたかう, 2:スキル, 3:にげる): ")

        if action == "1":  # たたかう
            print(f"\n{player_monster.name} の攻撃！")
            damage_to_enemy = calculate_damage(player_monster, enemy_monster)
            enemy_monster.hp -= damage_to_enemy
            print(f"{enemy_monster.name} に {damage_to_enemy} のダメージを与えた！")
            print(f"{enemy_monster.name} の残りHP: {max(0, enemy_monster.hp)}")
            if enemy_monster.hp <= 0:
                enemy_monster.is_alive = False
                print(f"\n{enemy_monster.name} を倒した！")
                break 

        elif action == "2":  # スキル
            if not player_monster.skills:
                print("覚えているスキルがない！")
                continue 

            print("\nどのスキルを使いますか？")
            for i, skill in enumerate(player_monster.skills):
                print(f"  {i + 1}: {skill.describe()}") 
            
            skill_choice_input = input(f"スキル番号を選んでください (1-{len(player_monster.skills)}, 0:キャンセル): ")

            if not skill_choice_input.isdigit():
                print("無効な入力です。数字で選んでください。")
                continue

            skill_choice = int(skill_choice_input)

            if skill_choice == 0:
                print("スキル使用をキャンセルしました。")
                continue 
            elif 1 <= skill_choice <= len(player_monster.skills):
                selected_skill = player_monster.skills[skill_choice - 1]
                
                target_for_skill = None
                if selected_skill.skill_type == "attack":
                    target_for_skill = enemy_monster
                elif selected_skill.skill_type in ["heal", "buff"] and selected_skill.target == "ally":
                    target_for_skill = player_monster 
                
                if target_for_skill:
                    apply_skill_effect(player_monster, target_for_skill, selected_skill) 
                    
                    if not enemy_monster.is_alive: 
                         print(f"\n{enemy_monster.name} を倒した！")
                         break 
                    
                    if not player_monster.is_alive: 
                         print(f"\n{player_monster.name} は倒れてしまった...")
                         break 
                else:
                    print(f"{selected_skill.name} は今は適切な対象に使えないようだ。")
                    continue 
            else:
                print("無効なスキル番号です。")
                continue 
        
        elif action == "3":  # にげる
            print(f"\n{player_monster.name} は逃げ出そうとした！")
            if random.random() < 0.75: 
                print("うまく逃げ切れた！")
                fled = True 
            else:
                print("しかし、回り込まれてしまった！逃げられない！")
        
        else:
            print("そのコマンドは存在しません。もう一度入力してください。")
            continue

        if not enemy_monster.is_alive or fled:
            break 

        print(f"\n{enemy_monster.name} の攻撃！")
        damage_to_player = calculate_damage(enemy_monster, player_monster)
        player_monster.hp -= damage_to_player
        print(f"{player_monster.name} は {damage_to_player} のダメージを受けた！")
        print(f"{player_monster.name} の残りHP: {max(0, player_monster.hp)}")
        if player_monster.hp <= 0:
            player_monster.is_alive = False
            print(f"\n{player_monster.name} は倒れてしまった...")
            break 
        
        if fled:
             break

        turn += 1
    
    print("\n----- 戦闘終了 -----")
    if fled: 
        print(f"{player_monster.name} は戦闘から離脱した。")
    elif player_monster.is_alive and not enemy_monster.is_alive: 
        print(f"{player_monster.name} は戦いに勝利した！")
        exp_reward = (enemy_monster.level * 10) + (enemy_monster.max_hp // 5)
        player_monster.gain_exp(exp_reward) 
    elif not player_monster.is_alive: 
        print(f"{player_monster.name} のパーティは全滅した...")
    else: 
        print("戦いは終わった。")

    # final_player_monster_state = player_monster
    # final_enemy_monster_state = enemy_monster
    # final_fled_flag = fled

    try:
        # print(f"[DEBUG battle.py] ATTEMPTING TO RETURN from start_battle (try block with ACTUAL Monster objects):")
        # print(f"[DEBUG battle.py]   player_monster type: {type(final_player_monster_state)}, name: {final_player_monster_state.name if final_player_monster_state else 'None'}, is_alive: {final_player_monster_state.is_alive if final_player_monster_state else 'N/A'}")
        # print(f"[DEBUG battle.py]   enemy_monster type: {type(final_enemy_monster_state)}, name: {final_enemy_monster_state.name if final_enemy_monster_state else 'None'}, is_alive: {final_enemy_monster_state.is_alive if final_enemy_monster_state else 'N/A'}")
        # print(f"[DEBUG battle.py]   fled type: {type(final_fled_flag)}, value: {final_fled_flag}")
        
        return_value = (player_monster, enemy_monster, fled) # 直接変数を返す
        # print(f"[DEBUG battle.py]   Return tuple type: {type(return_value)}")
        # if isinstance(return_value, tuple) and len(return_value) == 3:
        #     print(f"[DEBUG battle.py]     Item 0 type: {type(return_value[0])}")
        #     print(f"[DEBUG battle.py]     Item 1 type: {type(return_value[1])}")
        #     print(f"[DEBUG battle.py]     Item 2 type: {type(return_value[2])}")
        # else:
        #     print(f"[DEBUG battle.py]   !!! Return value is NOT a 3-element tuple: {return_value}")
            
        return return_value 
    except Exception as e:
        print(f"[DEBUG battle.py] !!! EXCEPTION DURING FINAL RETURN in start_battle (with ACTUAL Monster objects): {e}")
        # traceback.print_exc() # 必要であれば再度有効化
        return None 
