# モンスターRPG

Pythonで作られた小さなテキストベースRPGのプロトタイプです。SQLiteを利用してシンプルなセーブデータを保存し、複数のユーザーアカウントにも対応しています。最小構成のFlaskウェブサーバーも同梱されています。

> **補足**
> `docker-compose.yml` は Flask バックエンドを起動するだけで、PostgreSQL サービスは含まれていません。ゲームは引き続きローカルの SQLite データベース `monster_rpg_save.db` を利用します。

## 必要環境
- Python 3.11
- オプションのウェブサーバーを実行するには `Flask` が必要です。
- セーブデータには標準ライブラリの `sqlite3` モジュールを使用しています。

## セットアップとゲームの起動
1. (任意) Python 3.11 用の仮想環境を作成して有効化します。
2. 以下を実行してパッケージをインストールし、SQLiteデータベースを初期化します:
   ```bash
   pip install -e .
   python -m monster_rpg.database_setup
   ```
   既に存在しない場合 `monster_rpg_save.db` が作成されます。
   環境変数 `MONSTER_RPG_DB` を設定すると保存先を変更できます。
   デフォルトユーザー `player1` が自動で作成されます。追加ユーザーを作る場合は `database_setup.create_user()` を利用してください。
3. 代わりに簡易ウェブサーバーを起動するには:
   ```bash
   pip install -r requirements.txt
   python -m monster_rpg.webapp
   ```
   `webapp.py` は `/new_game` や `/load_game` といった最低限のJSON APIのみを提供し、戦闘機能は含まれていません。
4. `start_rpg.py` を使うと、完全なウェブ版を起動できます:
   ```bash
  pip install -r requirements.txt
  python -m monster_rpg.start_rpg
  ```
  これにより <http://localhost:5000/> でサーバーが起動し、Flaskテンプレートを使用した画面で戦闘を含む完全なゲームを楽しめます。
  `FLASK_SECRET_KEY` 環境変数を設定することで Flask の secret key を変更できます。未設定の場合は `dev-secret` が使用されます。

## Dockerでの実行

リポジトリには Flask バックエンドを SQLite で起動する `docker-compose.yml` が用意されています。以下のコマンドでイメージをビルドし、コンテナを起動します。

```bash
docker-compose build
docker-compose up
```

バックエンドサービスは5000番ポートを公開します。`./backend/src` をコンテナ内 `/app` としてマウントするため、コードの変更が即時反映されます。

## プロジェクト構成

### モンスター
- `monsters/monster_class.py` — `Monster` クラスと経験値・レベルアップ処理の補助関数を定義しています。
- `monsters/monster_data.py` — あらかじめ定義されたモンスターインスタンスと、ゲームで使用する辞書 `ALL_MONSTERS` を含みます。
- `monsters/__init__.py` — モンスターのクラスやデータを簡単にインポートできるよう公開しています。

`monsters/monsters.json` は JSON 形式のモンスター定義例です。`monster_loader.load_monsters()` を使うことで、ファイルからモンスターを一括読み込みできます。ファイルが存在しない、または JSON が不正な場合は `ValueError` が送出されます。

### スキルとアイテム
- `skills/skills.py` — `Skill` クラスを定義し、`skills/skills.json` からスキル情報を読み込みます。辞書 `ALL_SKILLS` に利用可能なスキルを格納します。
- `items/item_data.py` — `Item` クラスを定義し、`items/items.json` を読み込んで `ALL_ITEMS` を生成します。
- `skills/__init__.py` — ディレクトリをパッケージとして扱うための空モジュールです。

### マップ
- `map_data.py` — `Location` クラスと、各エリアの接続関係を示す辞書 `LOCATIONS` を定義します。 `STARTING_LOCATION_ID` がプレイヤーの初期位置です。各場所では、出現モンスターとその重みを設定する `enemy_pool` と、敵の数範囲を指定する `party_size` を利用できます。さらに、特定のアイテムが必要なエリアには `required_item` を設定できます。

例:

```json
{
  "enemy_pool": { "slime": 70, "goblin": 30 },
  "party_size": [1, 2]
}
```
アイテムが必要な場所の例:
```json
{
  "required_item": "celestial_feather",
  "connections": { "外縁へ戻る": "sky_isle" }
}
```

その他、`player.py` (プレイヤーデータとセーブ/ロード処理)、`battle.py` (戦闘システム)、`monsters/synthesis_rules.py` (モンスター合成レシピ) などのモジュールがあります。

## 新機能
- アイテムは戦闘外・戦闘中の両方で使用可能になりました。ポーションを使ってHPを回復し、戦況を覆しましょう。
- 最初の村にはショップがあり、スモールポーションやスライムの仲間を購入できます。
- 敵を倒すとアイテムを落とすことがあり、自動的に所持品に加わります。
- 基本的な装備のクラフト機能を追加しました。集めた素材から簡単な武器や防具を作成できます。
- 特定のレベルに達すると進化するモンスターもいます。
- 特定のアイテムとモンスターを組み合わせて新たなモンスターを生成できるようになりました。
- `/synthesize_action/<user_id>` API ではモンスター同士、モンスターとアイテム、アイテム同士のすべての合成を扱います。合成ページ(`/synthesize/<user_id>`)ではモーダルダイアログから素材を選択し、このエンドポイントに送信します。どちらのルートも同じJSON形式に対応しています。
- ウェブインターフェースでは最後の戦闘結果を表示するバトルログページを利用できます。
- ログインフォームからユーザー名とパスワードで認証できるようになりました。
- セーブ時にモンスターのHPとMPも保存されるため、続きから再開しても状態が維持されます。

## セーブについて
プレイヤーデータは `monster_rpg_save.db` に保存されます。環境変数 `MONSTER_RPG_DB` を使えばファイル名を変更できます。モンスターのHP/MPもセーブされるようになり、前回の状態を維持したまま再開できます。
ゲームをアップデートした際は `python -m monster_rpg.database_setup` を再実行するか、コード内で `database_setup.initialize_database()` を呼び出すことで、HP/MP列や `exploration_progress` テーブルなどの新しいデータが既存のセーブに追加されます。

## モンスター画像
モンスターの画像はローカルの `src/monster_rpg/static/images/` 以下に配置してください。リポジトリには空の `.gitkeep` ファイルのみ含め、大きな画像ファイルはGitにアップロードされないようにしています。
本プロジェクトにはモンスターの画像素材は付属していません。`monsters/monster_data.py` の `image_filename` に合わせ、`slime.png` や `wolf.png` などの名前で画像ファイルを用意してください。

## Tailwind CSS のビルド
`tailwind_src.css` を編集したら、次のコマンドでコンパイル済みスタイルシートを更新します:

```bash
npx tailwindcss -i src/monster_rpg/static/tailwind_src.css -o src/monster_rpg/static/tailwind.css
```

## テスト
`pytest` を実行する前に、パッケージを編集可能モードでインストールしてください:

```bash
pip install -e .
pytest
```

`make test` を使うと、インストールとテスト実行をまとめて行えます。

世界を冒険し、モンスターを育てる旅を楽しんでください！

## ライセンス
このプロジェクトは [MIT License](../LICENSE) のもとで公開されています。
