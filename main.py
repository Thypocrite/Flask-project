from flask import Flask, request, render_template, redirect, url_for, session, flash
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
            "select listmenu,liatprice from totall where user='"+user+"'")
        rows = cur.fetchall()
        return render_template('purchasehistory.html', rows=rows)
    else:
        return render_template('purchasehistory.html')


def get_product_details(product_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    # Query the database for the product details based on product_id
    sqlstr = "select product_id, title, price, image_url FROM products WHERE product_id='"+product_id+"'"
    cursor.execute(sqlstr)
    product = cursor.fetchone()
    # Close the database connection
    conn.close()

    if product:
        # Return the product details as a dictionary
        return {'product_id': product[0], 'title': product[1], 'price': product[2], 'image_url': product[3]}
    else:
        return None


@app.route("/test")
def test():
    return render_template("homepage.html")


@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    if 'user' not in session:
        return "<h1>您暫未登入， <br><a href = '/login'><b>" + \
            "點選這裡登入</b></a></h1>"

    product_id = request.form.get('product_id')
    # Fetch the product details based on product_id (you can use your existing get_product_details function)
    product_details = get_product_details(product_id)

    if product_details:
        # Check if a cart exists in the session, and initialize an empty cart if not
        if 'cart' not in session:
            session['cart'] = []

        if product_id not in session['cart']:
            cart_list = session['cart']
            # product_details['product_id'] = product_id
            cart_list.append(product_details)
            session['cart'] = cart_list
        return redirect(url_for('homepage'))
    else:
        return "Product not found"  # Handle the case where the product doesn't exist


@app.route('/cart')
def cart():
    user_cart = session.get('cart', [])
    return render_template('cart.html', cart=user_cart)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')

    if 'cart' in session:
        # Check if the 'cart' key exists in the session
        cart = session['cart']

        # Iterate through the cart and remove the product with the specified product_id
        for item in cart:
            if item['product_id'] == product_id:
                cart.remove(item)
                break  # Break the loop after removing the first matching product

        # Update the session with the modified cart
        session['cart'] = cart

    return redirect('/cart')  # Redirect back to the cart page after removal


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect('/cart')


@app.route('/check_session')
def check_session():
    # Check if a specific key (e.g., 'cart') exists in the session
    if 'cart' in session:
        # The session is not empty, 'cart' key exists
        return 'Session is not empty.'
    else:
        # The session is empty, 'cart' key does not exist
        return 'Session is empty.'


@app.route('/check_cart')
def check_cart():
    # Check if the 'cart' key exists in the session
    if 'cart' in session:
        # Get the cart data from the session
        cart_data = session['cart']
        # Print or log the cart data for inspection
        print(cart_data)
        # You can also return the cart data as a response to display it in the browser
        return f'Cart Data: {cart_data}'
    else:
        return 'Cart is empty.'


if __name__ == "__main__":
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
