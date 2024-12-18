from flask import Flask, render_template, \
    request, redirect, url_for, session
    
from dotenv import load_dotenv, dotenv_values

import requests
import os

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.globals.update(VKAPPID=os.getenv("VKAPPID"))
app.jinja_env.globals.update(REDIRECTURI=os.getenv("VKAUTHREDIRECT"))

@app.before_request
def make_session_permanent():
    session.permanent = True
    
    def template(tmpl_name, **kwargs):
        vk = False
        user_id = session.get('user_id')
        first_name = session.get('first_name')
        photo = session.get('photo')

        if user_id:
            vk = True

        return render_template(tmpl_name,
                            vk = vk,
                            user_id = user_id,
                            name = first_name,
                            photo = photo,
                            **kwargs)

@app.route("/")
def index():
    if session.get("user_id") != None:
        return render_template("vk.html", VKAUTHREDIRECT=os.getenv("VKAUTHREDIRECT"), VKAPPID=os.getenv("VKAPPID"), vk=True, photo=session["photo"], name=session["first_name"] + " " + session["last_name"])
    else:
        return render_template("vk.html", VKAUTHREDIRECT=os.getenv("VKAUTHREDIRECT"), VKAPPID=os.getenv("VKAPPID"), vk=False)

@app.route("/logout")
def logout():
    session.pop('user_id')
    session.pop('first_name')
    session.pop('last_name')
    session.pop('screen_name')
    session.pop('photo')

    return redirect(url_for('index'))

@app.route("/login")
def login():
    code = request.args.get("code")

    response = requests.get(f"https://oauth.vk.com/access_token?client_id={os.getenv("VKAPPID")}&redirect_uri={os.getenv("VKAUTHREDIRECT")}&client_secret={os.getenv("VKSECRET")}&code={code}")
    params = {
        "v": "5.101",
        "fields": "uid,first_name,last_name,screen_name,sex,bdate,photo_big",
        "access_token": response.json()['access_token']
    }

    get_info = requests.get(f"https://api.vk.com/method/users.get", params=params)
    get_info = get_info.json()['response'][0]

    session['user_id'] = get_info['id']
    session['first_name'] = get_info['first_name']
    session['last_name'] = get_info['last_name']
    session['screen_name'] = get_info['screen_name']
    session['photo'] = get_info['photo_big']


    return redirect(url_for('index'))