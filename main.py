from flask import Flask, request, render_template, redirect, url_for, session, flash
import re
from bs4 import BeautifulSoup
from datetime import date
import sqlite3

app = Flask(__name__)
app.secret_key = 'apple benanan key'


@app.route("/")
def index():
    return redirect(url_for("homepage"))


@app.route('/homepage')
def homepage():
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products LIMIT 12")
    products = cursor.fetchall()
    conn.close()
    return render_template("homepage.html", products=products)


@app.route('/membersonly/data')
def membersonly():
    if 'user' in session:
        user = session['user']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select * from lccnet where user='"+user+"'")
        records = cur.fetchone()
        email = records[1]
        name = records[3]
        phonenumber = records[4]
        birthday = records[5]
        address = records[6]
        return render_template('membersonly data.html', email=email, name=name, phonenumber=phonenumber, birthday=birthday, address=address)
    return "您暫未登入， <br><a href = '/login'></b>" + \
        "點選這裡登入</b></a>"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user' in session:
        user = session['user']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select * from lccnet where user='"+user+"'")
        records = cur.fetchone()
        name = records[3]
        if records[7] == "no":
            return render_template('administration.html')
        return render_template('membersonly.html', name=name)
    if request.method == 'POST':
        if request.form.get("reg") == "REGISTER":
            return redirect(url_for("reg"))
        user = request.form['user']
        passwd = request.form['passwd']

        conn = sqlite3.connect('merged.db')
        cursor = conn.cursor()
        sqlstr = "select passwd from lccnet where user='"+user+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            login_massage = "溫馨提示:用戶不存在,請先註冊"
            return render_template('login.html', message=login_massage)
        else:
            if data[0] == passwd:
                session['user'] = user
                connection = sqlite3.connect('merged.db')
                cur = connection.cursor().execute("select * from lccnet where user='"+user+"'")
                records = cur.fetchone()
                name = records[3]
                if records[7] == "no":
                    return render_template('administration.html')
                return render_template('membersonly.html', name=name)
            else:
                login_massage = "溫馨提示:密碼不正確,請確認"
                return render_template('login.html', message=login_massage)

    else:
        return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("login.html")


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        name = request.form['name']
        phonenumber = request.form['phonenumber']
        birthday = request.form['birthday']
        address = request.form['address']
        conn = sqlite3.connect('merged.db')
        cursor = conn.cursor().execute("INSERT INTO lccnet('user','passwd','name','phonenumber','birthday','address') values('" +
                                       user+"','"+passwd+"','"+name+"','"+phonenumber+"','"+birthday+"','"+address+"')")
        conn.commit()

        sqlstr = "select user from lccnet where user='"+user+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            reg_massage = "溫馨提示:註冊失敗"
            return render_template('reg.html', message=reg_massage)
        else:
            login_massage = "溫馨提示:帳號已註冊 請進行登入確認"
            return render_template('login.html', message=login_massage)
    else:
        return render_template('reg.html')


@app.route('/changePassword', methods=['POST', 'GET'])
def changePassword():
    if 'user' in session:
        user = session['user']
    if request.method == 'POST':
        orpasswd = request.form['orpasswd']
        nepasswd = request.form['nepasswd']
        passwdag = request.form['passwdag']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select passwd from lccnet where user='"+user+"'")
        records = cur.fetchone()
        print(records[0])
        if records[0] == orpasswd and records[0] != nepasswd and records[0] != passwdag[0] and nepasswd == passwdag:
            print(nepasswd)
            connection = sqlite3.connect('merged.db')
            user = session['user']
            cur = connection.cursor().execute("UPDATE lccnet SET passwd = '" +
                                              nepasswd+"' WHERE user = '"+user+"'")
            connection.commit()
            changePassword_massage = "溫馨提示:修改成功"
            return render_template('changePassword.html', message=changePassword_massage)
        elif nepasswd != passwdag:
            changePassword_massage = "溫馨提示:新密碼&確認密碼不相符"
            return render_template('changePassword.html', message=changePassword_massage)
        else:
            changePassword_massage = "溫馨提示:原始密碼不正確"
            return render_template('changePassword.html', message=changePassword_massage)
    else:
        return render_template('changePassword.html')


@app.route('/purchasehistory')
def purchasehistory():
    if 'user' in session:
        user = session['user']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute(
            "select * from totall where user='"+user+"'")
        rows = cur.fetchall()
        # 取得訂單標號
        cur = connection.cursor().execute(
            "select * from orders where user='"+user+"'")
        orders = cur.fetchall()
        return render_template('purchasehistory.html', rows=rows, orders=orders)
    else:
        return render_template('login.html')


@app.route('/administrationuser', methods=['POST', 'GET'])
def administrationuser():
    if request.form.get("memberrevise") == "memberrevise":
        return redirect(url_for("memberrevise"))
    if request.method == 'POST':
        member = request.form['member']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select * from lccnet where user='"+member+"'")
        rows = cur.fetchall()
        return render_template('administrationuser.html', rows=rows)
    else:
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select * from lccnet")
        rows = cur.fetchall()
        return render_template('administrationuser.html', rows=rows)


@app.route('/order', methods=['POST', 'GET'])
def order():
    if request.method == 'POST':
        ordernu = request.form['ordernu']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute(
            "select * from totall where order_id='"+ordernu+"'")
        rows = cur.fetchall()
        return render_template('order.html', rows=rows)
    else:
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute("select * from totall")
        rows = cur.fetchall()
        connection.commit()
        return render_template('order.html', rows=rows)


@app.route('/administrator', methods=['POST', 'GET'])
def administrator():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        name = request.form['name']
        phonenumber = request.form['phonenumber']
        birthday = request.form['birthday']
        address = request.form['address']
        password2 = "no"
        conn = sqlite3.connect('merged.db')
        cursor = conn.cursor().execute("INSERT INTO lccnet('user','passwd','name','phonenumber','birthday','address','password2') values('" +
                                       user+"','"+passwd+"','"+name+"','"+phonenumber+"','"+birthday+"','"+address+"','"+password2+"')")
        conn.commit()

        sqlstr = "select user from lccnet where user='"+user+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()
        if data == None:
            reg_massage = "溫馨提示:註冊失敗"
            return render_template('administrator.html', message=reg_massage)
        else:
            login_massage = "溫馨提示:帳號已註冊 請進行登入確認"
            return render_template('administrator.html', message=login_massage)
    else:
        return render_template('administrator.html')


def get_product_details(product_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    # Query the database for the product details based on product_id
    sqlstr = "select salePageId, title, price, image_url FROM products WHERE salePageId='"+product_id+"'"
    cursor.execute(sqlstr)
    product = cursor.fetchone()
    # Close the database connection
    conn.close()

    if product:
        # Return the product details as a dictionary
        return {'salePageId': product[0], 'title': product[1], 'price': product[2], 'image_url': product[3]}
    else:
        return None


@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"

    product_id = request.form.get('product_id')
    user = session['user']

    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT salePageId From carts WHERE user= ? and salePageId= ?", (user, str(product_id)))
    in_cart = cursor.fetchone()

    if not in_cart:
        # Fetch the product details based on product_id (you can use your existing get_product_details function)
        product_details = get_product_details(product_id)

        if product_details:

            salePageId = str(product_details.get('salePageId'))

            title = product_details.get('title')
            price = product_details.get('price')
            image_url = product_details.get('image_url')
            sqlstr = "INSERT INTO carts('salePageId','user','title','price','image_url') values('"+salePageId+"','" + \
                user+"','"+title+"','"+price+"','"+image_url+"')"
            cursor.execute(sqlstr)
            conn.commit()
            conn.close()

        return redirect(url_for('homepage'))
    else:
        return "<h1>商品已在您的購物車中 <br><a href = '/homepage'> <b>""回到首頁</b></a></h1>"


@app.route('/cart')
def cart():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"
    user = session['user']
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * From carts WHERE user='"+user+"'")
    cart_items = cursor.fetchall()
    conn.close()

    total_price = 0
    for item in cart_items:
        total_price += int(re.sub(r'[^\d.]', '', item[4]))

    total_price = str(total_price)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"

    product_id = request.form.get('product_id')
    user = session['user']

    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT salePageId From carts WHERE user= ? and salePageId= ?", (user, str(product_id)))
    in_cart = cursor.fetchone()

    if in_cart:
        cursor.execute(
            "DELETE FROM carts WHERE user= ? and salePageId= ?", (user, str(product_id)))
        conn.commit()
        conn.close()

    return redirect('/cart')  # Redirect back to the cart page after removal


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"
    user = session['user']
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    # Fetch cart items for the user from the database
    cursor.execute("SELECT * FROM carts WHERE user='"+user+"'")
    cart_items = cursor.fetchall()
    if cart_items:
        # Create a new order
        total_price = request.form.get("total_price")
        order_date = str(date.today())
        cursor.execute("INSERT INTO orders(user,total_price,order_date) Values(?, ?, ?)",
                       (user, total_price, order_date))
        # Get the order_id of the newly created order
        cursor.execute('SELECT last_insert_rowid()')
        order_id = cursor.fetchone()[0]

        # Transfer cart items to the user's inventory
        for item in cart_items:
            cursor.execute("INSERT INTO totall('salePageId','user','title','price','image_url',order_id,order_date) values(?, ?, ?, ?, ?, ?, ?)",
                           (item[1], item[2], item[3], item[4], item[5], order_id, order_date))

        # Clear the user's cart after checkout
        cursor.execute("DELETE FROM carts WHERE user='"+user+"'")
        conn.commit()
        conn.close()

        # Redirect to a thank you page or order summary page
        return render_template('checkout.html', cart_items=cart_items, total_price=total_price, order_id=order_id, order_date=order_date)
    else:
        return "<h1>您的購物車目前沒有商品， <br><a href = '/homepage'><b>" + \
            "前往購物</b></a></h1>"


@app.route('/clear_cart')
def clear_cart():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"
    user = session['user']

    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carts Where user='"+user+"'")
    conn.commit()
    conn.close()

    return redirect('/cart')


if __name__ == "__main__":
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
