# coding: utf-8

from bottle import route, run, get, post, request, template, redirect
import redis
import random, string
from hashlib import blake2b
import re

# Redisの用意
r = redis.Redis(host='localhost', port=6379, db=0)

title = 'Microsoft Teams Redirector'
timeout = 60 * 10   # seconds
password_digest = 'bc9ce810393f85d62d6715cba864d1f60cdd6000fdb80c5d8459556baac12b2a1124018871c02cefdad19ba167a61373e11466774b32b4dfcdbbd880fdfc9176'
# sample password: hogehoge
'''
    To generate password_digest value, pleaes follow these steps.
    1. $ python
    2. from hashlib import blake2b
    3. s = 'some string'
    4. blake2b(s.encode('utf-8')).hexdigest()
'''
validator = {}
validator['url'] = r'^https://teams.microsoft.com/[a-zA-Z0-9\.%/\?=-]+$'
validator['mid'] = r'[0-9]{8}'
validator['password'] = r'[a-zA-Z0-9!@#$%^&\*\(\)\-=_\+\[\]{}\\,\.<>;\':"`~]{,18}'

def gen_mid():
    '''
        8桁整数のランダムな会議IDを生成します。
    '''
    while True:
        mid = ''.join(random.choices(string.digits, k=8))

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
        return template('index', title=title, error=None)
    
    # 会議IDが存在しないものだったらエラー
    if not r.exists(mid):
        return template('index', title=title, error=f'指定された会議ID: { mid } は存在しません')
    
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
        
        items.append(item)
    
    # TTL順にソート
    items = sorted(items, key=lambda i: i['ttl'], reverse=True)
    return template('manage', title='会議の管理', items=items, mid=mid)


@post('/register')
def register():
    '''
        会議URL登録時に呼ばれます。
        登録成功時は管理画面にリダイレクトされます。
    '''
    url = request.forms.get('url')
    pw = request.forms.get('password')

    # Validate
    if not re.match(validator['url'], url):
        return template('error', title='Bad URL', message='URLが不正です')
    if not re.match(validator['password'], pw):
        return template('error', title='Bad Password', message='パスワードが不正です')

    # Check password
    if blake2b(pw.encode('utf-8')).hexdigest() != password_digest:
        return template('error', title='Wrong Password', message='パスワードが誤っています。')
    
    # Generate meeating id
    mid = gen_mid()
    r.set(mid, url)
    r.expire(mid, timeout)

    redirect('/manage')

run(host='localhost', port=8080, debug=True)
