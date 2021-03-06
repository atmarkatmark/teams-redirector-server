#!/usr/local/bin/python3
# coding: utf-8

from bottle import route, run, get, post, request, template, redirect
import redis
import random, string
from hashlib import blake2b
import re
from time import sleep

##############################
# 設定値
##############################
# Redis接続先
r = redis.Redis(host='localhost', port=6379, db=0)
# ページタイトル
title = '会議に参加する'
# 会議IDの有効時間(単位: 秒)
seconds_to_expire = [
    60 * 10, # 10 mins
    60 * 30  # 30 mins
]
# 会議登録パスワードのBlake2bダイジェスト値(初期値: hogehoge)
password_digest = 'bc9ce810393f85d62d6715cba864d1f60cdd6000fdb80c5d8459556baac12b2a1124018871c02cefdad19ba167a61373e11466774b32b4dfcdbbd880fdfc9176'
'''
    To generate password_digest value, pleaes follow these steps.
    1. $ python
    2. from hashlib import blake2b
    3. s = 'some string'
    4. blake2b(s.encode('utf-8')).hexdigest()
'''
# 設置ディレクトリの絶対パス(https://kuratsuki.net/some-prefix/)
path_prefix = ''
# 会議IDの桁数
id_length = 6

##############################
# Validator
##############################
validator = {}
# 登録可能なURL
validator['url'] = r'^https://teams.microsoft.com/[a-zA-Z0-9\.%/\?=-]+$'
# 会議IDの形式
validator['mid'] = f'[0-9]{{{id_length}}}'
# パスワード使用可能な文字
validator['password'] = r'[a-zA-Z0-9!@#$%^&\*\(\)\-=_\+\[\]{}\\,\.<>;\':"`~]{,18}'
# 有効期限
validator['expire'] = r'^[0-9]+$'

def gen_mid():
    '''
        n桁整数のランダムな会議IDを生成します。
        @ToDo: 上限数に達した時に無限ループになる
    '''
    while True:
        mid = ''.join(random.choices(string.digits, k=id_length))

        # 重複がなかったら終了
        if not r.exists(mid):
            break
        
        # break

    return mid


@route('/')
def index():
    mid = request.query.mid

    # 会議IDが指定されてなかったら普通のトップページ
    if not mid or not re.match(validator['mid'], mid):
        return template('index', title=title, error=None, path_prefix=path_prefix, id_len=id_length)
    
    # 会議IDが存在しないものだったらエラー
    if not r.exists(mid):
        return template('index', title=title, error=f'指定された会議ID: { mid } は存在しません', path_prefix=path_prefix, id_len=id_length)
    
    # 会議URLにリダイレクト
    url = r.get(mid).decode('utf-8')
    print(url)
    redirect(url)


@route('/manage', method=['GET', 'POST', 'CONNECT', 'HEAD'])
def manage(mid=False):
    '''
        登録された会議の一覧を表示します。
        新たな会議を登録するのもここから行います。
    '''
    items = []
    for k in r.keys():
        item = {
            'mid': k,
            'url': r.get(k),
            'ttl': r.ttl(k)
        }

        # TTLが１秒未満ならスキップ
        if item['ttl'] < 1:
            continue

        # TTLが598未満ならスキップ
        if item['ttl'] < 598:
            continue
        
        items.append(item)
    
    # TTL順にソート
    items = sorted(items, key=lambda i: i['ttl'], reverse=True)

    return template('manage', title='会議の管理', items=items, mid=mid, path_prefix=path_prefix, expire=seconds_to_expire)


@post('/register')
def register():
    '''
        会議URL登録時に呼ばれます。
        登録成功時は管理画面にリダイレクトされます。
    '''
    url = request.forms.get('url')
    pw = request.forms.get('password')
    expire = request.forms.get('expire')

    # Validate
    if not re.match(validator['url'], url):
        return template('error', title='Bad URL', message='URLが不正です', path_prefix=path_prefix)
    if not re.match(validator['password'], pw):
        return template('error', title='Bad Password', message='パスワードが不正です', path_prefix=path_prefix)
    if not re.match(validator['expire'], expire):
        return template('error', title='Bad Expiration', message='有効期間が不正です', path_prefix=path_prefix)

    # 連続登録を防ぐための簡易処置
    sleep(2)

    # Check password
    if blake2b(pw.encode('utf-8')).hexdigest() != password_digest:
        return template('error', title='Wrong Password', message='パスワードが誤っています。', path_prefix=path_prefix)
    
    # Generate meeating id
    mid = gen_mid()
    r.set(mid, url)
    r.expire(mid, expire)

    redirect(path_prefix + '/manage')

run(host='0.0.0.0', port=8080)
# run(server='cgi')
