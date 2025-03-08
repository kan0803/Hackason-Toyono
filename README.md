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

# フロントからバックを叩くには
localhost/api/<backendのパス>
っていう感じで
