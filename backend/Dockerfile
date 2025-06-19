# backend/Dockerfile

# ベースとなるPythonの公式イメージを指定
FROM python:3.11-slim

# コンテナ内での作業ディレクトリを設定
WORKDIR /app

# まず要件定義ファイルをコピーして、ライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY ./src /app

# 本番用のWSGIサーバーであるGunicornをインストール
RUN pip install gunicorn

# コンテナが起動したときに実行されるコマンド
# start_rpg.py の中にある Flaskのインスタンス(app)をGunicornで起動
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "monster_rpg.start_rpg:app"]
