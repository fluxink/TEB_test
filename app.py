from flask import Flask, redirect, url_for

from utils.database import get_user, init_db

app = Flask(__name__)

@app.route('/')
def index():
    return '<a href="/register">Register</a>'

@app.route('/register')
def register():
    return redirect("https://t.me/<your_bot_username_here>")

@app.route('/user/<telegram_id>')
def user(telegram_id):
    user = get_user(session, telegram_id)
    if user:
        return f'Hello, {user.name}!'
    else:
        return 'User not found'

if __name__ == '__main__':
    session = init_db()
    app.run(debug=True)
