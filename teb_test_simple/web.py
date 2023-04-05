import os
import hashlib
import hmac

from flask import Flask, redirect, url_for, request, make_response, \
    render_template

from database import get_user_by_tg_id, get_user, init_db


def check_tg_auth(auth_data, bot_token):
    auth_data = auth_data.copy()
    check_hash = auth_data.pop('hash')
    data_check_arr = []
    for key, value in auth_data.items():
        data_check_arr.append(f"{key}={value}")
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_value = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    print(hash_value)
    print(check_hash)
    if hash_value != check_hash:
        raise Exception('Data is NOT from Telegram')
    return auth_data

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
        try:
            auth_data = check_tg_auth(auth_data, os.getenv('API_TOKEN'))
        except Exception as e:
            return str(e)
        user = get_user_by_tg_id(session, auth_data['id'])
        if user:
            response = make_response(redirect(url_for('user', user_id=user.id)))
            for key, value in auth_data.items():
                response.set_cookie(key, value)
            return response
        else:
            return redirect(url_for('register'))
    elif cookies := check_parameters(request.cookies):
        try:
            cookies = check_tg_auth(cookies, os.getenv('API_TOKEN'))
        except Exception as e:
            return str(e)
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
        try:
            cookies = check_tg_auth(cookies, os.getenv('API_TOKEN'))
        except Exception as e:
            return str(e)
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
