# Monster RPG Backend

このプロジェクトは、シンプルなモンスターRPGのバックエンドシステムです。

## 起動方法

### 1. 必要なPythonパッケージのインストール
プロジェクトのルートディレクトリ（`monster_rpg_project`）で、以下のコマンドを実行して必要なパッケージをインストールします。

```bash
pip install Flask
```

### 2. ゲームの実行
以下のコマンドを実行してゲームを起動します。

```bash
python -m monster_rpg.start_rpg
```

### 3. ブラウザでのアクセス
ゲームが起動したら、ウェブブラウザで以下のURLにアクセスしてください。

```
http://127.0.0.1:5000/
```

### 開発者向け情報

*   **ソースコード:** `backend/src/monster_rpg/`
*   **テンプレート:** `backend/src/monster_rpg/templates/`
*   **静的ファイル (CSS, JS, 画像など):** `backend/src/monster_rpg/static/`
*   **モンスターデータ:** `backend/src/monster_rpg/monsters/monsters.json`
*   **アイテムデータ:** `backend/src/monster_rpg/items/items.json`
*   **装備データ:** `backend/src/monster_rpg/items/equipment.py`