# main.py
import random
from player import Player
from monsters import ALL_MONSTERS, Monster
from skills.skills import ALL_SKILLS
from battle import start_battle
from map_data import LOCATIONS, Location # Locationもインポート
from database_setup import initialize_database, DATABASE_NAME

# initialize_database() # main実行時に毎回呼ぶより、初回セットアップや専用スクリプトが良いかも

def get_monster_instance_for_battle(monster_id_or_object):
    """
    戦闘用にモンスターの新しいインスタンスを返す。
    引数がIDの場合はALL_MONSTERSからコピーを生成。
    引数がMonsterオブジェクトの場合はそのコピーを生成。
    """
    if isinstance(monster_id_or_object, str):
        monster_id = monster_id_or_object.lower()
        if monster_id in ALL_MONSTERS:
            # ALL_MONSTERSのテンプレートから新しいインスタンスをコピー
            battle_monster = ALL_MONSTERS[monster_id].copy()
            # 戦闘開始時の状態をリセット
            battle_monster.hp = battle_monster.max_hp
            battle_monster.is_alive = True
            # battle_monster.status_effects = [] # 必要なら状態異常もリセット
            return battle_monster
        else:
            print(f"エラー: モンスターID '{monster_id}' は存在しません。")
            return None
    elif isinstance(monster_id_or_object, Monster):
        # 渡されたMonsterオブジェクトのコピーを作成して戦闘に使用
        battle_monster = monster_id_or_object.copy()
        battle_monster.hp = battle_monster.max_hp # HPを最大にリセット
        battle_monster.is_alive = True
        return battle_monster
    else:
        print(f"エラー: 不正な引数です - {monster_id_or_object}")
        return None


def game_loop(hero: Player): # 型ヒントを追加
    """ゲームのメインループ"""
    game_over = False
    
    while not game_over:
        current_location_data = LOCATIONS.get(hero.current_location_id)
        if not current_location_data:
            print(f"エラー: 現在地ID '{hero.current_location_id}' が見つかりません。ゲームを終了します。")
            game_over = True
            break
            
        # Locationオブジェクトであることを確認 (map_data.pyのLOCATIONSがLocationインスタンスを保持するように変更した場合)
        # もしLOCATIONSが辞書のままなら、current_location_data['name'] のようにアクセス
        current_location_name = current_location_data.name if isinstance(current_location_data, Location) else current_location_data.get('name', "不明な場所")
        current_location_description = current_location_data.description if isinstance(current_location_data, Location) else current_location_data.get('description', "")


        print(f"\n現在地: {current_location_name} ({hero.name} Lv.{hero.player_level})")
        print(current_location_description)

        # 行動選択
        print("\nどうしますか？")
        print("1: 移動する")
        print("2: ステータス確認 (主人公)")
        print("3: パーティ確認 (モンスター)")
        print("4: モンスター合成") # 新しい選択肢
        
        # 宿屋のチェック (Locationオブジェクトに属性があるか確認)
        if isinstance(current_location_data, Location) and hasattr(current_location_data, 'has_inn') and current_location_data.has_inn:
            inn_cost = current_location_data.inn_cost if hasattr(current_location_data, 'inn_cost') else 10 # デフォルトコスト
            print(f"8: 宿屋に泊まる ({inn_cost}G)")
        
        print("9: ゲームをセーブ")
        print("0: ゲーム終了")

        action = input("行動を選んでください (番号): ")

        if action == "1": # 移動
            if not isinstance(current_location_data, Location) or not current_location_data.connections:
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
                    new_location_name = new_location_data.name if isinstance(new_location_data, Location) else new_location_data.get('name', "不明な場所")
                    print(f"{new_location_name} へ移動しました。")

                    # エンカウント判定 (Locationオブジェクトの属性を確認)
                    if isinstance(new_location_data, Location) and \
                       new_location_data.possible_enemies and \
                       random.random() < new_location_data.encounter_rate:
                        
                        print("\n!!!モンスターに遭遇した!!!")
                        enemy_id = new_location_data.get_random_enemy_id()
                        
                        if enemy_id and hero.party_monsters:
                            enemy_for_battle = get_monster_instance_for_battle(enemy_id)
                            if not enemy_for_battle:
                                print("エラー: 敵モンスターの準備に失敗しました。")
                                continue

                            # 戦闘に参加するプレイヤーモンスターを選択 (先頭の生存モンスター)
                            player_monster_for_battle = None
                            for monster in hero.party_monsters:
                                if monster.is_alive:
                                    player_monster_for_battle = get_monster_instance_for_battle(monster) # コピーを渡す
                                    break
                            
                            if not player_monster_for_battle:
                                print("戦えるモンスターがパーティにいません！")
                                continue
                            
                            # player_monster_for_battle は既にコピーなので、元のモンスターの状態は戦闘に影響されない。
                            # 戦闘結果（経験値、HPなど）を元のモンスターに反映する必要がある。
                            original_player_monster_in_party = None
                            for m in hero.party_monsters: # 元のパーティから戦闘参加モンスターを見つける
                                if m.monster_id == player_monster_for_battle.monster_id and m.hp == player_monster_for_battle.hp: # より確実な同定方法が必要かも
                                    original_player_monster_in_party = m
                                    break
                            
                            if not original_player_monster_in_party: # 万が一見つからない場合 (通常ありえないが)
                                print("エラー：戦闘参加モンスターをパーティ内で特定できませんでした。")
                                continue


                            battle_result_player_monster, battle_result_enemy_monster, fled = start_battle(player_monster_for_battle, enemy_for_battle)
                            
                            # 戦闘結果を元のパーティモンスターに反映
                            original_player_monster_in_party.hp = battle_result_player_monster.hp
                            original_player_monster_in_party.exp = battle_result_player_monster.exp
                            original_player_monster_in_party.level = battle_result_player_monster.level
                            original_player_monster_in_party.max_hp = battle_result_player_monster.max_hp
                            original_player_monster_in_party.attack = battle_result_player_monster.attack
                            original_player_monster_in_party.defense = battle_result_player_monster.defense
                            original_player_monster_in_party.is_alive = battle_result_player_monster.is_alive
                            # スキルやステータス効果の変動もあればここで反映

                            # プレイヤーモンスターがレベルアップした場合、hero.party_monsters内のインスタンスが直接更新されているはず
                            # (gain_expメソッドがselfを変更するため)

                        elif not hero.party_monsters:
                            print("手持ちモンスターがいない！逃げるしかない！")
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
            hero.show_all_party_monsters_status() # 番号で選びやすくするため表示

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

                # (オプション) 合成アイテムの選択
                # item_to_use = None
                # if hero.items:
                # print("合成に使用するアイテムを選びますか？ (y/n)")
                # ... アイテム選択処理 ...
                
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
            if isinstance(current_location_data, Location) and hasattr(current_location_data, 'has_inn') and current_location_data.has_inn:
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
    initialize_database() # データベース初期化を一度だけ行う
    print("モンスターRPGへようこそ！")

    hero = None
    load_choice = input("セーブデータをロードしますか？ (y/n): ").lower()
    if load_choice == 'y':
        hero = Player.load_game(DATABASE_NAME)

    if not hero:
        player_name = input("主人公の名前を入力してください: ")
        hero = Player(name=player_name, gold=100) # 初期ゴールド設定
        print(f"冒険をはじめます、{hero.name}！")
        # 初期モンスターを仲間にする (例)
        if "slime" in ALL_MONSTERS:
             hero.add_monster_to_party("slime") # スライムを初期メンバーに
        if "goblin" in ALL_MONSTERS:
             hero.add_monster_to_party("goblin") # ゴブリンも初期メンバーに
        # hero.save_game(DATABASE_NAME) # ニューゲーム時にセーブするなら

    if hero:
        game_loop(hero)
    else:
        print("プレイヤーの作成またはロードに失敗しました。ゲームを開始できません。")

if __name__ == "__main__":
    main()
