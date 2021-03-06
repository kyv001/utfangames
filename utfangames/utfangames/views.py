# -*- coding:utf-8 -*-

from flask import (render_template,
                   redirect,
                   request,
                   session,
                   url_for,
                   send_from_directory)
from . import app
from .models import *
import os

@app.route('/')
def home():
    return render_template("index.html",
                           games=Game.query.all(),
                           os=os,
                           math=__import__("math"),
                           len=len)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        author = Author.query.filter_by(
            name=request.form.get("name"),
            password=request.form.get("password"))
        if len(list(author)) == 0:
            return render_template("login.html", err="用户名或密码不正确！", title="登录")
        session["id"] = author[0].id
        session["name"] = author[0].name
        return redirect(url_for('home'))
    return render_template("login.html", title="登录")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 测试有没有重名
        author = Author.query.filter_by(
            name=request.form.get("name"))
        if len(list(author)) > 0:
            return render_template("signup.html", err="用户名已存在！", title="注册")
        new_author = Author()
        new_author.name = request.form.get("name")
        new_author.password = request.form.get("password")
        path = os.path.join(
            os.getcwd(),
            "utfangames/static/users/{}/games".replace('/', os.sep).format(new_author.name))
        os.makedirs(path)
        db.session.add(new_author)
        db.session.commit()
        
        # 注册完了，自动登录
        author = Author.query.filter_by(
            name=request.form.get("name"),
            password=request.form.get("password"))
        session["id"] = author[0].id
        session["name"] = author[0].name
        return redirect(url_for('home'))
    return render_template("signup.html", title="注册")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session["id"]
    del session["name"]
    return redirect(url_for('home'))

@app.route('/newgame', methods=['GET', 'POST'])
def newgame():
    if request.method == 'POST':
        if session.get("id"):
            # 测试有没有重名
            game = Game.query.filter_by(
                name=request.form.get("name"))
            if len(list(game)) > 0:
                return render_template("newgame.html", err="游戏名已存在！", title="创建新游戏")
            # 测试有没有图片传进来
            if not request.files["image"]:
                return render_template("newgame.html", err="请选择封面图！", title="创建新游戏")
            newgame = Game()
            newgame.author_id = session["id"]
            newgame.intro = request.form.get("intro")
            file = request.files["file"]
            image = request.files["image"]

            dirpath = os.path.join(
                os.getcwd(),
                "utfangames/static/users/{}/games/{}".replace('/', os.sep).format(
                    session["name"],
                    request.form.get("name")
                    ))
            os.makedirs(dirpath)
            path = os.path.join(dirpath, file.filename)
            imgpath = os.path.join(dirpath, image.filename)
            newgame.path = path
            newgame.imgpath = imgpath
            newgame.name = request.form.get("name")
            file.save(path)
            image.save(imgpath)
            db.session.add(newgame)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template("newgame.html", title="创建新游戏")

@app.route("/downloads/<id>")
def download(id):
    game = Game.query.get(id)
    dirpath = os.path.join(
        os.getcwd(),
        "utfangames/static/users/{}/games/{}".replace('/', os.sep).format(
            game.author.name,
            game.name
            ))
    filename = game.path.split(os.sep)[-1]
    return send_from_directory(dirpath, filename, as_attachment=True)

@app.route("/game/<id>")
def game(id):
    game = Game.query.get(id)
    return render_template("game.html", game=game, os=os, title=game.name)

@app.route("/user/<id>")
def user(id):
    user = Author.query.get(id)
    return render_template("user.html",
                           user=user,
                           os=os,
                           title=user.name,
                           math=__import__("math"),
                           len=len)

@app.route("/delete/<id>")
def delete(id):
    if session.get("id"):
        game = Game.query.get(int(id.split("_")[0]))
        if game.author.id == session.get("id"):
            db.session.delete(game)
            db.session.commit()
            dirpath = os.path.join(
                os.getcwd(),
                "utfangames/static/users/{}/games/{}/".replace('/', os.sep).format(
                    session.get("name"),
                    game.name
                    ))
            for root, dirs, files in os.walk(dirpath, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            print(dirpath[:-1], "\a")
            os.rmdir(dirpath)
 
            # os.walk的第一个参数是要遍历并删除子文件夹和文件的目录
            # 上面的代码运行后，文件夹"1"里的文件夹和文件全被删除，但是文件夹"1"还存在
            # 具体可以查下os.walk()的用法，以及其参数topdown的功能
            # 这一段代码来自blog.csdn.net/kaida1234/article/details/89553115，好人一生平安
    return redirect(url_for('home'))

@app.route('/changegame/<id>', methods=['GET', 'POST'])
def changegame(id):
    if request.method == 'POST':
        if session.get("id"):
            game = Game.query.get(id)
            db.session.delete(game)
            db.session.commit()
            dirpath = os.path.join(
                os.getcwd(),
                "utfangames/static/users/{}/games".replace('/', os.sep).format(
                    session.get("name")
                    ))
            for root, dirs, files in os.walk(dirpath, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

            newgame = Game()
            newgame.author_id = session["id"]
            newgame.intro = request.form.get("intro")
            file = request.files["file"]
            image = request.files["image"]

            dirpath = os.path.join(
                os.getcwd(),
                "utfangames/static/users/{}/games/{}".replace('/', os.sep).format(
                    session["name"],
                    request.form.get("name")
                    ))
            os.makedirs(dirpath)
            path = os.path.join(dirpath, file.filename)
            imgpath = os.path.join(dirpath, image.filename)
            newgame.path = path
            newgame.imgpath = imgpath
            newgame.name = request.form.get("name")
            file.save(path)
            image.save(imgpath)
            db.session.add(newgame)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template("changegame.html", id=id, title="改编游戏")

@app.route('/search')
def search():
    value = request.args.get("value")
    games = None
    if value:
        games = Game.query.filter(Game.name.like("%{}%".format(value))).all()
    return render_template("search.html",
                           games=games,
                           os=os,
                           math=__import__("math"),
                           len=len,
                           title="搜索",
                           value=value)
