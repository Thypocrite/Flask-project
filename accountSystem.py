import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from flask import Flask, redirect, url_for, request, render_template
import sqlite3
app = Flask(__name__)


def window():
    app = QApplication(sys.argv)
    widget = QWidget()

    textLabel = QLabel(widget)
    textLabel.setText("註冊失敗 !(mail已被註冊) 請回上一頁重新進行操作")
    textLabel.move(110, 65)

    widget.setGeometry(50, 50, 500, 150)
    widget.setWindowTitle("貼心小提示")
    widget.setWindowFlags(Qt.WindowStaysOnTopHint)
    widget.show()
    sys.exit(app.exec_())


@app.route("/")
def index():
    return redirect(url_for("homepage"))


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form.get("reg") == "REGISTER":
            return redirect(url_for("reg"))
        user = request.form['user']
        passwd = request.form['passwd']

        conn = sqlite3.connect('LR.db')
        cursor = conn.cursor()

        sqlstr = "select passwd from lccnet where user='"+user+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            return "帳號不存在"
        else:
            if data[0] == passwd:
                return redirect("http://www.yahoo.com.tw")
            else:
                return "密碼不正確"
    else:
        return render_template('login.html')


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        name = request.form['name']
        phonenumber = request.form['phonenumber']
        address = request.form['address']

        conn = sqlite3.connect('LR.db')
        cursor = conn.cursor()

        sqlstr = "INSERT INTO lccnet('user','passwd','name','phonenumber','address') values('" + \
            user+"','"+passwd+"','"+name+"','"+phonenumber+"','"+address+"')"
        cursor.execute(sqlstr)
        conn.commit()

        sqlstr = "select passwd from lccnet where user='"+user+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            return window()
        else:
            return render_template('membersonly.html')
    else:
        return render_template('reg.html')


if __name__ == '__main__':
    app.run()
