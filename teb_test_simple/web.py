import os
import hashlib
import hmac

from flask import Flask, redirect, url_for, request, make_response, \
    render_template

from database import get_user_by_tg_id, get_user, init_db


def check_tg_auth(data, bot_token):
    auth_data = data.copy()
    hash_received = auth_data.pop('hash')
    sorted_data = sorted(auth_data.items())
    data_str = '\n'.join([f'{key}={value}' for key, value in sorted_data])
    hashed_bot_token = hashlib.sha256(bot_token.encode()).digest()
    hmac_signature = hmac.new(hashed_bot_token, msg=data_str.encode(), digestmod=hashlib.sha256).hexdigest()

    return hmac_signature == hash_received

def check_parameters(source) -> dict:
    auth_data = {}
    for key, value in source.items():
        auth_data[key] = value

    if ('id' not in auth_data or
        'hash' not in auth_data):
        return None
    
    return auth_data

app = Flask(__name__)

@app.route('/')
def index():

    if auth_data := check_parameters(request.args):
        if not check_tg_auth(auth_data, os.getenv('API_TOKEN')):
            return 'Wrong hash'
        user = get_user_by_tg_id(session, auth_data['id'])
        if user:
            response = make_response(redirect(url_for('user', user_id=user.id)))
            for key, value in auth_data.items():
                response.set_cookie(key, value)
            return response
        else:
            return redirect(url_for('register'))
    elif cookies := check_parameters(request.cookies):
        if not check_tg_auth(cookies, os.getenv('API_TOKEN')):
            return 'Wrong hash'
        user = get_user_by_tg_id(session, cookies['id'])
        if user:
            return redirect(url_for('user', user_id=user.id))
        else:
            return redirect(url_for('register'))
    else:
        response = make_response(render_template('index.html.jinja'))
        return response

@app.route('/register')
def register():
    return redirect("https://t.me/kingdomcome_bot?start=start")

@app.route('/user/<user_id>')
def user(user_id):
    if cookies := check_parameters(request.cookies):
        if not check_tg_auth(cookies, os.getenv('API_TOKEN')):
            return 'Wrong hash'
        user = get_user(session, user_id)
        if user.telegram_id == cookies['id']:
            return render_template('user.html.jinja', user=user, cookies=cookies)
        else:
            return redirect(url_for('register'))
    else:
        return redirect(url_for('register'))

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    for key in request.cookies:
        response.set_cookie(key, '', expires=0)
    return response

if __name__ == '__main__':
    session = init_db()
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 80))
