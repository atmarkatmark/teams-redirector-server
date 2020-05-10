# Teams-Redirector

Microsoft Teamsの会議に未登録ゲストを招待するのを補助するためのWebサービスです。

## いきさつ

Microsoft Teamsには未登録のゲストを招待する機能があります。
招待する手順は次の通りです。

1. 会議を開催する
1. 会議の参加者を表示する
1. 招待リンクをコピーする
1. 招待リンクを相手に送る

招待リンクを受け取った側はリンクから会議に参加します。
招待された会議へは、Microsoft Teamsに登録していなくてもゲストとして参加できます。

1. 招待リンクを開く
1. 名前を入力する
1. 参加申請を行う

参加申請を行うと、会議の主催者は許可を求められます。
主催者が許可することで参加が完了します。

ここで問題になるのが招待リンクです。
招待リンクはハイパーリンク付きのリッチテキストでクリップボードにコピーされます。
そのため、HTMLメールに対応していないと送ることができません。

またテキスト部分にURLが書かれていないため、URLを取り出すにはWordなどのリッチテキストに対応したエディタに一度貼り付けてから取り出す必要があります。
これらの手順を簡略化し、会議へのゲスト招待を行いやすくするのが本ソフトウェアの主目的です。

## しくみ

1. 招待リンクを貼り付けることで、含まれているURLを抽出します(Vue.js)
1. 登録を行うとランダムな8桁の数字を生成して、URLを結びつけます(Bottle, Redis)
1. 会議主催者は8桁の数字をゲスト参加者に伝えます
1. ゲスト参加者は8桁の数字を入力します(Bottle)
1. 8桁の数字に対応したURLへリダイレクトされます(Redis, Bottle)

## 使い方

### 前提とする環境

* Nginx等(リバースプロキシとして使う)
* Docker
* docker-compose

### 環境作成

```bash
$ git clone https://github.com/atmarkatmark/teams-redirector-server.git
$ cd teams-redirector-server
$ sudo docker-compose build --no-cache
$ sudo docker-compose up -d
```

デフォルトではTCP/3007で待ち受けます。
Nginx等でアクセスを振り分けてください。

NginxでのSSLを使う設定例は次の通りです。

```
upstream teams {
        server 127.0.0.1:8007;
}

server {
        listen 80;
        server_name teams.kuratsuki.net;
        return 301 https://$host$request_uri;
}
server {
        listen 443 ssl;
        ssl_certificate     /etc/letsencrypt/live/dev.kuratsuki.net/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/dev.kuratsuki.net/privkey.pem;
        root /var/www/html;
        server_name teams.kuratsuki.net;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        location / {
                proxy_pass http://teams;
        }
}
```

### 環境削除

```bash
$ cd teams-redirector-server
$ sudo docker-compose rm -sf
```

## 注意事項

デフォルトでは10分間だけ会議URLを保持します。
