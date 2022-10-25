from flask import Flask, render_template, request, redirect, url_for
from flask import session

from secrets import token_hex

from requests import get, put

app = Flask(__name__,
            static_url_path='',
            static_folder='static',)
app.secret_key = token_hex(20)

admin_id = "admin"
admin_pw = str(token_hex(15))

print(f"ADMIN ID: {admin_id}")
print(f"ADMIN PW: {admin_pw}")

season = 1

api_url = "http://localhost:8000"

@app.route('/')
def index():
    if "id" not in session or "pw" not in session:
        print("LOGIN FAILED: NOT LOGGED IN")
        return redirect(url_for('login'))
    if session["id"] == admin_id and session["pw"] == admin_pw:
        return render_template('index.html', season=season)
    else:
        print("LOGIN FAILED: DIFFERENT ID/PW")
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form.get("id") and request.form.get("pw"):
            session['id'] = request.form.get("id")
            session['pw'] = request.form.get("pw")
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('pw', None)
    return redirect(url_for('login'))


@app.route('/get-season')
def get_season():
    return season


@app.route('/set-season', methods=['POST'])
def set_season():
    if session["id"] == admin_id and session["pw"] == admin_pw:
        global season
        season = int(request.args.get("season"))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/set-score', methods=['POST'])
def set_score():
    if session["id"] == admin_id and session["pw"] == admin_pw:
        # set score by rest api
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/get-score', methods=['POST'])
def get_score():
    if session["id"] == admin_id and session["pw"] == admin_pw:
        get(f"{api_url}/get-score")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))
