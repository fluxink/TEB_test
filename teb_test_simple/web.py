import os
from typing import Dict, Union

from flask import Flask, redirect, url_for, request, \
    make_response, render_template

from database import get_user_by_tg_id, get_user, init_db
from services import (
    data_check_str,
    check_parameters,
    generate_session_id,
)


API_TOKEN = os.getenv('API_TOKEN')
BOT_URL = os.getenv('BOT_URL')
BOT_LOGIN = os.getenv('BOT_LOGIN')
SITE_URL = os.getenv('SITE_URL')

app = Flask(__name__)
sessions: Dict[str, Dict[str, Union[str, int]]] = {}

def authorizhed(func):
    def wrapper(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        if session_id and sessions.get(session_id):
            return func(*args, **kwargs)
        return redirect(url_for('index'))

    return wrapper

@app.route('/')
def index() -> Union[str, redirect, make_response, render_template]:
    if auth_data := check_parameters(request.args):
        if not data_check_str(auth_data, API_TOKEN):
            return 'Wrong hash'
        user = get_user_by_tg_id(sql_session, auth_data['id'])
        if user:
            response = make_response(redirect(url_for('user')))
            session_id = generate_session_id()
            sessions[session_id] = {
                'id': user.id,
                'photo_url': auth_data.get('photo_url'),
            }
            response.set_cookie('session_id', session_id)
            return response
        else:
            return redirect(url_for('register'))
    elif request.cookies.get('session_id'):
        return redirect(url_for('user'))

    return render_template('index.html.jinja', data_telegram_login=BOT_LOGIN, data_auth_utl=SITE_URL)

@app.route('/register')
def register() -> redirect:
    return redirect(BOT_URL)

@app.route('/user')
@authorizhed
def user() -> Union[str, redirect]:
    user = get_user(sql_session, sessions[request.cookies.get('session_id')]['id'])
    if user:
        return render_template('user.html.jinja', user=user)
    return redirect(url_for('index'))

@app.route('/logout')
def logout() -> make_response:
    response = make_response(redirect(url_for('index')))
    if session_id := request.cookies.get('session_id'):
        sessions.pop(session_id, None)
    for key in request.cookies:
        response.set_cookie(key, '', expires=0)
    return response

if __name__ == '__main__':
    sql_session = init_db()
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 80))
