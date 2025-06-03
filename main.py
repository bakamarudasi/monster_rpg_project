# main.py
import random
from player import Player
from monsters import ALL_MONSTERS, Monster
from skills.skills import ALL_SKILLS
from battle import start_battle # battle.py から start_battle をインポート
from map_data import LOCATIONS, Location 
from database_setup import initialize_database, DATABASE_NAME

def get_monster_instance_copy(monster_id_or_object: Monster | str) -> Monster | None:
    """
    モンスターの新しいインスタンス（コピー）を返します。
    引数がIDの場合はALL_MONSTERSからコピーを生成。
    引数がMonsterオブジェクトの場合はそのコピーを生成。
    戦闘開始時や仲間に加える際に使用します。
    """
    if isinstance(monster_id_or_object, str):
        monster_id = monster_id_or_object.lower()
        if monster_id in ALL_MONSTERS:
            # ALL_MONSTERSのテンプレートから新しいインスタンスをコピー
            new_monster = ALL_MONSTERS[monster_id].copy()
            if new_monster:
                # 戦闘や仲間にする際の初期状態（HP最大など）
                new_monster.hp = new_monster.max_hp
                new_monster.is_alive = True
            return new_monster
        else:
            print(f"エラー: モンスターID '{monster_id}' は存在しません。")
            return None
    elif isinstance(monster_id_or_object, Monster):
        # 渡されたMonsterオブジェクトのコピーを作成
        new_monster = monster_id_or_object.copy()
        if new_monster:
            new_monster.hp = new_monster.max_hp # HPを最大にリセット
            new_monster.is_alive = True
        return new_monster
    else:
        print(f"エラー: 不正な引数です - {monster_id_or_object}")
        return None

def generate_enemy_party(location: Location) -> list[Monster]:
    """指定された場所に基づいて敵パーティを生成します (1〜3体)。"""
    enemy_party = []
    if not location.possible_enemies:
        return enemy_party

    num_enemies = random.randint(1, min(3, len(location.possible_enemies))) # 最大3体まで、または出現可能数まで

    for _ in range(num_enemies):
        enemy_id = random.choice(location.possible_enemies)
        enemy_instance = get_monster_instance_copy(enemy_id)
        if enemy_instance:
            enemy_party.append(enemy_instance)
    
    # 万が一、インスタンス生成に失敗して空になった場合も考慮
    if not enemy_party and location.possible_enemies: # 敵がいるはずなのに空なら1体は保証
        enemy_id = random.choice(location.possible_enemies)
        enemy_instance = get_monster_instance_copy(enemy_id)
        if enemy_instance:
            enemy_party.append(enemy_instance)
            
    return enemy_party


def game_loop(hero: Player): # 型ヒントを追加
    """ゲームのメインループ"""
    game_over = False
    
    while not game_over:
        current_location_data = LOCATIONS.get(hero.current_location_id)
        if not current_location_data:
            print(f"エラー: 現在地ID '{hero.current_location_id}' が見つかりません。ゲームを終了します。")
            game_over = True
            break
            
        current_location_name = current_location_data.name
        current_location_description = current_location_data.description


        print(f"\n現在地: {current_location_name} ({hero.name} Lv.{hero.player_level})")
        print(current_location_description)

        # 行動選択
        print("\nどうしますか？")
        print("1: 移動する")
        print("2: ステータス確認 (主人公)")
        print("3: パーティ確認 (モンスター)")
        print("4: モンスター合成") 
        
        if hasattr(current_location_data, 'has_inn') and current_location_data.has_inn:
            inn_cost = current_location_data.inn_cost if hasattr(current_location_data, 'inn_cost') else 10
            print(f"8: 宿屋に泊まる ({inn_cost}G)")
        
        print("9: ゲームをセーブ")
        print("0: ゲーム終了")

        action = input("行動を選んでください (番号): ")

        if action == "1": # 移動
            if not current_location_data.connections:
                print("ここからはどこへも行けないようだ。")
                continue

            print("\nどちらへ移動しますか？")
            possible_moves = list(current_location_data.connections.items())
            
            for i, (direction_command, destination_id) in enumerate(possible_moves):
                destination_name = LOCATIONS.get(destination_id).name if LOCATIONS.get(destination_id) else "不明な場所"
                print(f"  {i + 1}: {direction_command} ({destination_name} へ)")
            print(f"  0: 移動をやめる")

            move_choice_input = input("移動先を選んでください (番号): ")
            if not move_choice_input.isdigit():
                print("無効な入力です。")
                continue
            
            move_choice = int(move_choice_input)

            if move_choice == 0:
                continue
            elif 1 <= move_choice <= len(possible_moves):
                _, destination_id = possible_moves[move_choice - 1]
                hero.current_location_id = destination_id
                new_location_data = LOCATIONS.get(hero.current_location_id)
                if new_location_data:
                    new_location_name = new_location_data.name
                    print(f"{new_location_name} へ移動しました。")

                    if new_location_data.possible_enemies and \
                       random.random() < new_location_data.encounter_rate:
                        
                        print("\n!!!モンスターに遭遇した!!!")
                        
                        # --- 3vs3戦闘のためのパーティ準備 ---
                        # プレイヤーの戦闘参加パーティ (生存している先頭最大3体のコピー)
                        # battle.py 側でコピーや生存確認をするので、ここではhero.party_monstersをそのまま渡す
                        player_battle_party = hero.party_monsters 

                        # 敵パーティを生成
                        enemy_battle_party = generate_enemy_party(new_location_data)
                        
                        if not player_battle_party: # プレイヤーのパーティが空の場合
                            print("手持ちモンスターがいない！逃げるしかない！")
                            continue # 戦闘せずにループの最初へ
                        
                        if not enemy_battle_party: # 敵パーティが生成されなかった場合
                            print("モンスターは現れたが、すぐに去っていったようだ...")
                            continue # 戦闘せずにループの最初へ
                        
                        # --- 戦闘開始 ---
                        battle_outcome_result_str = start_battle(player_battle_party, enemy_battle_party, hero)
                        
                        # 戦闘結果の処理
                        if battle_outcome_result_str == "win":
                            print(f"{hero.name} は勝利をおさめた！")
                            # 経験値やアイテム獲得はbattle.py内で処理済み（player_battle_partyの要素が更新される）
                        elif battle_outcome_result_str == "lose":
                            print(f"{hero.name} は敗北してしまった...")
                            # TODO: ゲームオーバー処理など
                        elif battle_outcome_result_str == "fled":
                            print(f"{hero.name} は戦闘から逃げ出した。")
                        else: # draw や予期せぬ結果
                            print("戦闘は不思議な形で終了した...")
                        
                        # 戦闘でHPなどが変わったモンスターの状態をhero.party_monstersに反映させる必要はない
                        # なぜなら、player_battle_party は hero.party_monsters の参照であり、
                        # battle.py 内でその要素（モンスターオブジェクト）の属性が直接変更されるため。

                    elif not new_location_data.possible_enemies:
                         print("この場所にはモンスターはいないようだ。")
                    else:
                        print("モンスターは現れなかったようだ...")
                else:
                    print(f"エラー: 移動先の場所ID '{hero.current_location_id}' が見つかりません。")
            else:
                print("無効な移動先です。")

        elif action == "2": # ステータス確認
            hero.show_status()
        
        elif action == "3": # パーティ確認
            hero.show_all_party_monsters_status()

        elif action == "4": # モンスター合成
            if len(hero.party_monsters) < 2:
                print("合成するにはモンスターが2体以上必要です。")
                continue

            print("\nどのモンスターを合成しますか？ パーティから2体選んでください。")
            hero.show_all_party_monsters_status() 

            try:
                idx1_input = input(f"1体目のモンスター番号 (1-{len(hero.party_monsters)}): ")
                if not idx1_input.isdigit(): raise ValueError("数字で入力してください。")
                monster1_idx = int(idx1_input) - 1

                idx2_input = input(f"2体目のモンスター番号 (1-{len(hero.party_monsters)}): ")
                if not idx2_input.isdigit(): raise ValueError("数字で入力してください。")
                monster2_idx = int(idx2_input) - 1
                
                if not (0 <= monster1_idx < len(hero.party_monsters) and \
                        0 <= monster2_idx < len(hero.party_monsters)):
                    print("無効な番号です。")
                    continue
                if monster1_idx == monster2_idx:
                    print("同じモンスターは選べません。")
                    continue
                
                success, message, new_monster = hero.synthesize_monster(monster1_idx, monster2_idx)
                print(message)
                if success and new_monster:
                    print(f"{new_monster.name} のステータス:")
                    new_monster.show_status()

            except ValueError as e:
                print(f"入力エラー: {e}")
            except Exception as e:
                print(f"合成中に予期せぬエラーが発生しました: {e}")
        
        elif action == "8": # 宿屋
            if hasattr(current_location_data, 'has_inn') and current_location_data.has_inn:
                cost = current_location_data.inn_cost if hasattr(current_location_data, 'inn_cost') else 10
                hero.rest_at_inn(cost)
            else:
                print("ここには宿屋はありません。")

        elif action == "9": # セーブ
            hero.save_game(DATABASE_NAME)

        elif action == "0": # ゲーム終了
            print("ゲームを終了します。お疲れ様でした！")
            game_over = True
        else:
            print("無効なコマンドです。")


def main():
    initialize_database() 
    print("モンスターRPGへようこそ！")

    hero = None
    load_choice = input("セーブデータをロードしますか？ (y/n): ").lower()
    if load_choice == 'y':
        hero = Player.load_game(DATABASE_NAME)

    if not hero:
        player_name = input("主人公の名前を入力してください: ")
        hero = Player(name=player_name, gold=100) 
        print(f"冒険をはじめます、{hero.name}！")
        if "slime" in ALL_MONSTERS:
             hero.add_monster_to_party("slime") 
        if "goblin" in ALL_MONSTERS:
             hero.add_monster_to_party("goblin")
        if "wolf" in ALL_MONSTERS: # 3体目の初期メンバー例
             hero.add_monster_to_party("wolf")


    if hero:
        game_loop(hero)
    else:
        print("プレイヤーの作成またはロードに失敗しました。ゲームを開始できません。")

if __name__ == "__main__":
    main()
