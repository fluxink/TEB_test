import os
import hashlib
import urllib.parse
import hmac
import uuid

from flask import Flask, redirect, url_for, request, make_response, \
    render_template

from database import get_user_by_tg_id, get_user, init_db


def check_tg_auth(auth_data, bot_token):
    auth_data = auth_data.copy()
    true_hash = auth_data.pop('hash')
    if 'photo_url' in auth_data:
        auth_data['photo_url'] = urllib.parse.unquote(auth_data['photo_url'])
    
    tg_data = "\n".join([f'{k}={auth_data[k]}' for k in sorted(auth_data)])
    tg_data = tg_data.encode()
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash = hmac.new(secret_key, tg_data, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(hash.encode(), true_hash.encode())

def check_parameters(source) -> dict:
    auth_data = {}
    for key, value in source.items():
        auth_data[key] = value

    if ('id' not in auth_data or
        'hash' not in auth_data):
        return None
    
    return auth_data

def generate_session_id():
    return str(uuid.uuid4())

app = Flask(__name__)
session = {}

@app.route('/')
def index():

    if auth_data := check_parameters(request.args):
        if not check_tg_auth(auth_data, os.getenv('API_TOKEN')):
            return 'Wrong hash'
        user = get_user_by_tg_id(sql_session, auth_data['id'])
        if user:
            response = make_response(redirect(url_for('user')))
            session_id = generate_session_id()
            session[session_id] = {
                'id': user.id,
                'photo_url': auth_data.get('photo_url'),
            }
            response.set_cookie('session_id', session_id)
            return response
        else:
            return redirect(url_for('register'))
    elif request.cookies.get('session_id'):
        return redirect(url_for('user'))
    else:
        response = make_response(render_template('index.html.jinja'))
        return response

@app.route('/register')
def register():
    return redirect("https://t.me/kingdomcome_bot?start=start")

@app.route('/user')
def user():
    if request.cookies.get('session_id'):
        if user_session := session.get(request.cookies.get('session_id')):
            user = get_user(sql_session, user_session['id'])
            return render_template('user.html.jinja', user=user, photo_url=user_session['photo_url'])
        else:
            return redirect(url_for('logout'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    if request.cookies.get('session_id'):
        session.pop(request.cookies.get('session_id'))
    for key in request.cookies:
        response.set_cookie(key, '', expires=0)
    return response

if __name__ == '__main__':
    sql_session = init_db()
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 80))
