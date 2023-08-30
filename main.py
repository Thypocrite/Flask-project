from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("homepage"))


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route("/profile/<username>")
def profile(username):
    return "welcome %s" % username


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("register") == "register":
            return redirect(url_for("register"))
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()

        sqlstr = "select password from members where username='"+username+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            return "帳號不存在"
        else:
            if data[0] == password:
                return redirect(url_for("profile", username=username))
            else:
                return "密碼不正確"

    else:
        return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()

        sqlstr = "INSERT INTO members('username','password','email') values('" + \
            username+"','"+password+"','"+email+"')"
        cursor.execute(sqlstr)
        conn.commit()

        sqlstr = "select password from members where username='"+username+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            return "註冊失敗"
        else:
            return "註冊成功"
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
