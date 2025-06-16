# main.py
import random
from ..player import Player
from ..monsters import ALL_MONSTERS, Monster
from ..skills.skills import ALL_SKILLS
from ..battle import start_battle  # battle.py から start_battle をインポート
from ..map_data import LOCATIONS, Location, display_map, load_locations
from ..database_setup import initialize_database, DATABASE_NAME
from ..items.item_data import ALL_ITEMS
from ..exploration import (
    show_exploration_progress,
    get_monster_instance_copy,
    generate_enemy_party,
)
from ..shop import open_shop
from ..battle_manager import handle_battle_loss


def game_loop(hero: Player):  # 型ヒントを追加
    """ゲームのメインループ"""
    if not LOCATIONS:
        load_locations()

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
        print("5: 探索する")
        print("6: アイテムを使う")
        if getattr(current_location_data, "has_shop", False):
            print("7: ショップで買い物")

        if hasattr(current_location_data, "has_inn") and current_location_data.has_inn:
            inn_cost = (
                current_location_data.inn_cost
                if hasattr(current_location_data, "inn_cost")
                else 10
            )
            print(f"8: 宿屋に泊まる ({inn_cost}G)")

        print("9: ゲームをセーブ")
        print("10: マップを見る")
        print("11: モンスター図鑑")
        print("0: ゲーム終了")

        action = input("行動を選んでください (番号): ")

        if action == "1":  # 移動
            if not current_location_data.connections:
                print("ここからはどこへも行けないようだ。")
                continue

            print("\nどちらへ移動しますか？")
            possible_moves = list(current_location_data.connections.items())

            for i, (direction_command, destination_id) in enumerate(possible_moves):
                dest = LOCATIONS.get(destination_id)
                destination_name = dest.name if dest else "不明な場所"
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
                new_location_data = LOCATIONS.get(destination_id)
                req = (
                    getattr(new_location_data, "required_item", None)
                    if new_location_data
                    else None
                )
                if req and not any(it.item_id == req for it in hero.items):
                    print(f"そこへ行くには {req} が必要だ。")
                    continue
                hero.current_location_id = destination_id
                new_location_data = LOCATIONS.get(hero.current_location_id)
                if new_location_data:
                    new_location_name = new_location_data.name
                    print(f"{new_location_name} へ移動しました。")

                    if (
                        new_location_data.enemy_pool
                        or new_location_data.possible_enemies
                    ) and random.random() < new_location_data.encounter_rate:
                        print("\n!!!モンスターに遭遇した!!!")

                        # --- 3vs3戦闘のためのパーティ準備 ---
                        # プレイヤーの戦闘参加パーティ (生存している先頭最大3体のコピー)
                        # battle.py 側でコピーや生存確認をするので、ここではhero.party_monstersをそのまま渡す
                        player_battle_party = hero.party_monsters

                        # 敵パーティを生成
                        enemy_battle_party = new_location_data.create_enemy_party()

                        if not player_battle_party:  # プレイヤーのパーティが空の場合
                            print("手持ちモンスターがいない！逃げるしかない！")
                            continue  # 戦闘せずにループの最初へ

                        if not enemy_battle_party:  # 敵パーティが生成されなかった場合
                            print("モンスターは現れたが、すぐに去っていったようだ...")
                            continue  # 戦闘せずにループの最初へ

                        # --- 戦闘開始 ---
                        battle_outcome_result_str = start_battle(
                            player_battle_party, enemy_battle_party, hero
                        )

                        # 戦闘結果の処理
                        if battle_outcome_result_str == "win":
                            print(f"{hero.name} は勝利をおさめた！")
                            # 経験値やアイテム獲得はbattle.py内で処理済み（player_battle_partyの要素が更新される）
                        elif battle_outcome_result_str == "lose":
                            print(f"{hero.name} は敗北してしまった...")
                            result = handle_battle_loss(hero)
                            if result == "exit":
                                game_over = True
                        elif battle_outcome_result_str == "fled":
                            print(f"{hero.name} は戦闘から逃げ出した。")
                        else:  # draw や予期せぬ結果
                            print("戦闘は不思議な形で終了した...")

                        # 戦闘でHPなどが変わったモンスターの状態をhero.party_monstersに反映させる必要はない
                        # なぜなら、player_battle_party は hero.party_monsters の参照であり、
                        # battle.py 内でその要素（モンスターオブジェクト）の属性が直接変更されるため。

                    elif (
                        not new_location_data.enemy_pool
                        and not new_location_data.possible_enemies
                    ):
                        print("この場所にはモンスターはいないようだ。")
                    else:
                        print("モンスターは現れなかったようだ...")
                else:
                    print(f"エラー: 移動先の場所ID '{hero.current_location_id}' が見つかりません。")
            else:
                print("無効な移動先です。")

        elif action == "2":  # ステータス確認
            hero.show_status()

        elif action == "3":  # パーティ確認
            hero.show_all_party_monsters_status()

        elif action == "4":  # モンスター合成
            if len(hero.party_monsters) < 2:
                print("合成するにはモンスターが2体以上必要です。")
                continue

            print("\nどのモンスターを合成しますか？ パーティから2体選んでください。")
            hero.show_all_party_monsters_status()

            try:
                idx1_input = input(f"1体目のモンスター番号 (1-{len(hero.party_monsters)}): ")
                if not idx1_input.isdigit():
                    raise ValueError("数字で入力してください。")
                monster1_idx = int(idx1_input) - 1

                idx2_input = input(f"2体目のモンスター番号 (1-{len(hero.party_monsters)}): ")
                if not idx2_input.isdigit():
                    raise ValueError("数字で入力してください。")
                monster2_idx = int(idx2_input) - 1

                if not (
                    0 <= monster1_idx < len(hero.party_monsters)
                    and 0 <= monster2_idx < len(hero.party_monsters)
                ):
                    print("無効な番号です。")
                    continue
                if monster1_idx == monster2_idx:
                    print("同じモンスターは選べません。")
                    continue

                success, message, new_monster = hero.synthesize_monster(
                    monster1_idx, monster2_idx
                )
                print(message)
                if success and new_monster:
                    print(f"{new_monster.name} のステータス:")
                    new_monster.show_status()

            except ValueError as e:
                print(f"入力エラー: {e}")
            except Exception as e:
                print(f"合成中に予期せぬエラーが発生しました: {e}")

        elif action == "5":  # 探索する
            progress_before = hero.get_exploration(hero.current_location_id)
            gained = random.randint(15, 30)
            progress_after = hero.increase_exploration(hero.current_location_id, gained)
            print(f"探索を行った！ (+{gained}%)")
            show_exploration_progress(progress_after)
            if progress_before < 100 <= progress_after:
                if getattr(current_location_data, "hidden_connections", {}):
                    current_location_data.connections.update(
                        current_location_data.hidden_connections
                    )
                    print("新たな道が開けた！")
                if getattr(current_location_data, "boss_enemy_id", None):
                    print("ボスが姿を現した！")
                    boss = get_monster_instance_copy(
                        current_location_data.boss_enemy_id
                    )
                    if boss:
                        outcome = start_battle(hero.party_monsters, [boss], hero)
                        if outcome == "win":
                            print("ダンジョンを制覇した！")
                            current_location_data.boss_enemy_id = None
                        elif outcome == "lose":
                            print(f"{hero.name} はボスに敗北してしまった...")
                            res = handle_battle_loss(hero)
                            if res == "exit":
                                game_over = True
                                break
                        elif outcome == "fled":
                            print(f"{hero.name} はボスから逃げ出した。")

            if random.random() < getattr(current_location_data, "event_chance", 0):
                if random.random() < 0.5 and getattr(
                    current_location_data, "treasure_items", []
                ):
                    item_id = random.choice(current_location_data.treasure_items)
                    if item_id in ALL_ITEMS:
                        hero.items.append(ALL_ITEMS[item_id])
                        print(f"宝箱を見つけた！{ALL_ITEMS[item_id].name} を手に入れた。")
                elif getattr(current_location_data, "rare_enemies", []):
                    print("レアモンスターが現れた！")
                    rare_id = random.choice(current_location_data.rare_enemies)
                    rare_enemy = get_monster_instance_copy(rare_id)
                    if rare_enemy:
                        outcome = start_battle(hero.party_monsters, [rare_enemy], hero)
                        if outcome == "win":
                            print(f"{hero.name} はレアモンスターを倒した！")
                        elif outcome == "lose":
                            print(f"{hero.name} は敗北してしまった...")
                            res = handle_battle_loss(hero)
                            if res == "exit":
                                game_over = True
                                break
                        elif outcome == "fled":
                            print(f"{hero.name} は戦闘から逃げ出した。")
            elif (
                current_location_data.enemy_pool
                or current_location_data.possible_enemies
            ) and random.random() < current_location_data.encounter_rate:
                print("\n!!!モンスターが襲ってきた!!!")
                player_battle_party = hero.party_monsters
                enemy_battle_party = current_location_data.create_enemy_party()
                if enemy_battle_party:
                    battle_outcome_result_str = start_battle(
                        player_battle_party, enemy_battle_party, hero
                    )
                    if battle_outcome_result_str == "win":
                        print(f"{hero.name} は勝利した！")
                    elif battle_outcome_result_str == "lose":
                        print(f"{hero.name} は敗北してしまった...")
                        res = handle_battle_loss(hero)
                        if res == "exit":
                            game_over = True
                            break
                    elif battle_outcome_result_str == "fled":
                        print(f"{hero.name} は戦闘から逃げ出した。")
                else:
                    print("敵は現れなかった...")

        elif action == "6":
            if not hero.items:
                print("アイテムを持っていない。")
                continue
            hero.show_items()
            idx_in = input(f"使うアイテム番号 (1-{len(hero.items)}, 0でキャンセル): ")
            if not idx_in.isdigit():
                print("数字で入力してください。")
                continue
            idx = int(idx_in)
            if idx == 0:
                continue
            if not (1 <= idx <= len(hero.items)):
                print("無効な番号です。")
                continue
            if not hero.party_monsters:
                print("モンスターがいない。")
                continue
            hero.show_all_party_monsters_status()
            t_in = input(f"対象モンスター番号 (1-{len(hero.party_monsters)}): ")
            if not t_in.isdigit():
                print("数字で入力してください。")
                continue
            t_idx = int(t_in) - 1
            if not (0 <= t_idx < len(hero.party_monsters)):
                print("無効な番号です。")
                continue
            hero.use_item(idx - 1, hero.party_monsters[t_idx])

        elif action == "7":
            open_shop(hero, current_location_data)

        elif action == "8":  # 宿屋
            if (
                hasattr(current_location_data, "has_inn")
                and current_location_data.has_inn
            ):
                cost = (
                    current_location_data.inn_cost
                    if hasattr(current_location_data, "inn_cost")
                    else 10
                )
                hero.rest_at_inn(cost)
            else:
                print("ここには宿屋はありません。")

        elif action == "9":  # セーブ
            hero.save_game(DATABASE_NAME)

        elif action == "10":
            display_map()

        elif action == "11":
            hero.monster_book.show_book()

        elif action == "0":  # ゲーム終了
            print("ゲームを終了します。お疲れ様でした！")
            game_over = True
        else:
            print("無効なコマンドです。")


def main():
    initialize_database()
    load_locations()
    print("モンスターRPGへようこそ！")

    hero = None
    load_choice = input("セーブデータをロードしますか？ (y/n): ").lower()
    if load_choice == "y":
        hero = Player.load_game(DATABASE_NAME)

    if not hero:
        player_name = input("主人公の名前を入力してください: ")
        hero = Player(name=player_name, gold=100)
        print(f"冒険をはじめます、{hero.name}！")
        if "slime" in ALL_MONSTERS:
            hero.add_monster_to_party("slime")
        if "goblin" in ALL_MONSTERS:
            hero.add_monster_to_party("goblin")
        if "wolf" in ALL_MONSTERS:  # 3体目の初期メンバー例
            hero.add_monster_to_party("wolf")

    if hero:
        game_loop(hero)
    else:
        print("プレイヤーの作成またはロードに失敗しました。ゲームを開始できません。")


if __name__ == "__main__":
    main()
