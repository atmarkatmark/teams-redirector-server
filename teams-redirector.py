# coding: utf-8

from bottle import route, run, post, request, template
import redis
import random, string

r = redis.Redis(host='localhost', port=6379, db=0)
print(r.get('foo'))
r.set('foo', 'bar')
r.expire('foo', 10) # will disappear in 10 seconds
r.set('hoge', 'hoge')
print(r.exists('hogee'))
print(r.exists('hoge'))

def gen_key():
    key = ''.join(random.choices(string.digits, k=8))
    return key

for i in range(10):
    print(gen_key())

@route('/')
def index():
    return template('index', title='Microsoft Teams Redirector')

@route('/start/<id:int>')
def start(id):
    v = r.get('hoge')
    return f'<p>Starting { id }... { v }</p>'

@post('/register')
def register():
    url = request.forms.get('url')
    pw = request.forms.get('password')
    return f'url: { url } \n password { pw }'

run(host='localhost', port=8080, debug=True)
