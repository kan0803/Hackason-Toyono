# Hackason-Toyono
豊能ハッカソン

# 環境の使い方(Docker環境ある人用)

## 起動と動作確認
1. Docker Desktop起動
2. コンテナ立ち上げ
以下のコマンドを実行
```shell
Hackason-Toyono $ docker compose up --build -d
```
3. コンテナに入る
```shell
Hackason-Toyono $ docker exec -it toyono-hackathon-python bash 
```
4. コンテナの中でプログラム動かしてみる．

表示内容人によって違うかも．
```shell
root@9c0d9ce5907d:/app# ls
main.py
root@9c0d9ce5907d:/app# python3 main.py 
test
root@9c0d9ce5907d:/app# 
```
