# coding: utf-8

from bottle import route, run, get, post, request, template, redirect
# import redis
import random, string
from hashlib import blake2b
import re

# r = redis.Redis(host='localhost', port=6379, db=0)
# print(r.get('foo'))
# r.set('foo', 'bar')
# r.expire('foo', 10) # will disappear in 10 seconds
# r.set('hoge', 'hoge')
# print(r.exists('hogee'))
# print(r.exists('hoge'))

password_digest = blake2b('hogehoge'.encode('utf-8')).hexdigest()
validator = {}
validator['url'] = r'https://teams.microsoft.com'
validator['id'] = r'[0-9]{8}'
validator['password'] = r'[a-zA-Z0-9!@#$%^&\*\(\)\-=_\+\[\]{}\\,\.<>;\':"`~]{,18}'

def gen_id():
    while True:
        id = ''.join(random.choices(string.digits, k=8))

        # # 重複がなかったら終了
        # if not r.exists(id):
        #     break
        
        break

    return id

@route('/')
def index():
    return template('index', title='Microsoft Teams Redirector')

@route('/manage')
def manage():
    items = []
    items.append({ 'id': '12345678', 'ttl': 100, 'url': 'https://www.google.co.jp/' })
    items.append({ 'id': '23456789', 'ttl': 32, 'url': 'https://www.yahoo.co.jp/' })
    return template('manage', title='会議の管理', items=items)

@get('/start')
def start():
    id = request.forms.get('id')
    # if not r.exists(id):
    #     return template('error', title="ID Not Exist", message=f'ID: { id } が存在していません。')
    # url = r.get(id)
    url = 'https://www.google.co.jp/'
    redirect(url)

@post('/register')
def register():
    url = request.forms.get('url')
    pw = request.forms.get('password')

    if blake2b(pw.encode('utf-8')).hexdigest() != password_digest:
        return template('error', title='Wrong Password', message='パスワードが誤っています。')
    
    return template('registered', id=gen_id())

run(host='localhost', port=8080, debug=True)
