# main.py (大幅に修正)
import random # エンカウント判定で使用
from player import Player
from monsters import ALL_MONSTERS, Monster # Monsterクラスもインポート
from skills.skills import ALL_SKILLS # (もしスキルデータが必要なら)
from battle import start_battle
from map_data import LOCATIONS # LOCATIONS辞書をインポート

def get_monster_instance_for_battle(monster_id):
    """戦闘用にモンスターの新しいインスタンス（または状態リセット済み）を返す"""
    if monster_id in ALL_MONSTERS:
        original_monster = ALL_MONSTERS[monster_id]
        # 戦闘のたびに新しいインスタンスを作るか、deepcopyするのが安全
        # ここでは簡単な例として、主要なステータスをコピーして新しいインスタンスを作る
        # Monsterクラスの__init__の引数に合わせて調整してください
        battle_monster = Monster(
            name=original_monster.name,
            hp=original_monster.max_hp, # HPは最大値で初期化
            attack=original_monster.attack,
            defense=original_monster.defense,
            level=original_monster.level,
            exp=original_monster.exp, # expはそのまま引き継ぐか、戦闘用には不要か
            element=original_monster.element,
            skills=original_monster.skills, # スキルリストもコピー (Skillオブジェクトが変更されないなら参照でも可)
            growth_type=original_monster.growth_type
        )
        battle_monster.is_alive = True # 生存状態もリセット
        return battle_monster
    return None


def game_loop(hero):
    """ゲームのメインループ"""
    game_over = False
    while not game_over:
        current_location = LOCATIONS[hero.current_location_id]
        

        print(f"\n 現在地: {current_location.name} ({hero.name} Lv.{hero.player_level})") # 現在地とプレイヤー情報
        print(current_location.description)

        # 行動選択
        print("\nどうしますか？")
        if hasattr(current_location, 'has_inn') and current_location.has_inn:
            print(f"4: 宿屋に泊まる ({current_location.inn_cost}G)") # コマンド番号は適宜調整

        print("1: 移動する")
        print("2: ステータス確認")
        print("3: パーティ確認") # 手持ちモンスターのステータス確認
        
        # print("9: ゲーム終了") # 将来的にはセーブなど

        action = input("行動を選んでください (番号): ")

        if action == "1": # 移動
            print("\nどちらへ移動しますか？")
            possible_moves = list(current_location.connections.items()) # [("方向コマンド", "行き先ID"), ...]
            
            if not possible_moves:
                print("ここからはどこへも行けないようだ。")
                continue

            for i, (direction_command, destination_id) in enumerate(possible_moves):
                destination_name = LOCATIONS[destination_id].name
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
                new_location = LOCATIONS[hero.current_location_id]
                print(f"{new_location.name} へ移動しました。")

                # --- エンカウント判定 ---
                if new_location.possible_enemies and random.random() < new_location.encounter_rate:
                    print("\n!!!モンスターに遭遇した!!!")
                    
                    enemy_id = new_location.get_random_enemy_id()
                    if enemy_id and hero.party_monsters: # 敵がいて、パーティにもモンスターがいる
                        
                        # 戦闘用の敵モンスターインスタンスを取得 (HPなどをリセット)
                        enemy_for_battle = get_monster_instance_for_battle(enemy_id)
                        if not enemy_for_battle:
                            print("エラー: 敵モンスターの準備に失敗しました。")
                            continue

                        # 戦闘に参加するプレイヤーモンスターを選択 (今は先頭のモンスター)
                        # こちらも戦闘ごとにHPなどをリセットするのが望ましい
                        player_monster_original = hero.party_monsters[0]
                        player_monster_for_battle = get_monster_instance_for_battle(player_monster_original.name.lower()) # 名前で呼び出す想定
                        if not player_monster_for_battle: # もし名前で見つからない場合の代替
                             player_monster_for_battle = Monster(**vars(player_monster_original)) # 簡易コピー
                             player_monster_for_battle.hp = player_monster_original.hp # 現在のHPを引き継ぐか、max_hpか
                             player_monster_for_battle.is_alive = player_monster_original.is_alive
                             # 必要なら player_monster_original.hp = player_monster_original.max_hp のように全回復させてから戦闘も

                        if not player_monster_for_battle.is_alive:
                            print(f"{player_monster_for_battle.name} は戦える状態ではありません！")
                            # パーティの次のモンスターを選ぶロジックなどが必要
                            continue
                        
                        start_battle(player_monster_for_battle, enemy_for_battle)
                        
                        # 戦闘後のプレイヤーモンスターステータスを元のパーティ情報に反映する必要がある
                        # 例えば、経験値やHPの変動など。
                        # 今回は player_monster_for_battle の結果は元の player_monster_original には自動で反映されない。
                        # 簡単な対応としては、戦闘後にIDなどで探し出して更新するか、
                        # Playerクラスのparty_monstersリストに格納されているオブジェクトを直接start_battleに渡す
                        # (ただし、その場合はstart_battle内でHPなどを戦闘開始時に適切に設定する必要がある)
                        # -- 現状のstart_battleは引数で渡されたオブジェクトを直接変更するので、
                        #    元のparty_monstersのオブジェクトを渡せば戦闘結果は反映されるが、
                        #    戦闘開始時のHPリセットなどをbattle.py側でしっかり行う必要がある。
                        #    ここでは、簡略化のため、直接party_monsters[0]を渡すことを一旦考える。
                        #    ただし、その場合、戦闘開始時にHPをリセットする必要がある。
                        #    battle.pyのstart_battleの冒頭で、player_monster.hp = player_monster.max_hp のような処理が必要。
                        #    敵モンスターも同様。

                    elif not hero.party_monsters:
                        print("手持ちモンスターがいない！逃げるしかない！")
                    else:
                        print("モンスターは現れなかったようだ...") # possible_enemiesが空などの場合
            else:
                print("無効な移動先です。")

        elif action == "2": # ステータス確認
            hero.show_status()
        
        elif action == "3": # パーティ確認
            hero.show_all_party_monsters_status()

        # elif action == "9": # ゲーム終了
        #     print("ゲームを終了します。")
        #     game_over = True
        else:
            print("無効なコマンドです。")


def main():
    # 主人公作成
    hero = Player(name="ユーシャ", gold=100)
    # 初期手持ちモンスター (テスト用)
    if "slime" in ALL_MONSTERS:
         # 戦闘用に毎回インスタンスを作る方が安全だが、ここでは簡略化
        initial_slime = get_monster_instance_for_battle("slime")
        if initial_slime:
            hero.add_monster_to_party(initial_slime)

    # ゲームループ開始
    game_loop(hero)

if __name__ == "__main__":
    main()