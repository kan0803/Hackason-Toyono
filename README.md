# Hackason-Toyono
豊能ハッカソン
# ディレクトリ構成
## frontend
- 構成はvue+nginxです．現状は元のvueアプリです
- 割り当てポートは8080
## backend
- python
- fastAPIとopenCVが最低限入っています
- 割り当てポートは8000
- moduleディレクトリ内でいい感じの関数実装してもらったら，APIにその関数を割り当てたら叩けるようになります．

# 起動方法と確認方法(Vue＋FastAPI+nginx全体の立ち上げ)
1. DockerDesktop起動
2. コンテナ立ち上げ
```bash
Hackason-Toyono $ docker compose up --build
```
3. ページにアクセスしてみる
以下のリンクにアクセスしてみてください
- localhost:8080
  - vueの画面が表示されたらおk
- localhost:8000
  - hello world的なやつが表示されればおk

# CLIからコンテナに入る方法
pythonを叩きたい時，サーバーの中で何かを確認したいときなど
```
$ docker exec -it <コンテナ名 or コンテナID> bash
例）　docker exec -it hackason-toyono-backend bash
```


# フロントからバックを叩くには
localhost/api/<backendのパス>
っていう感じで叩けます．
