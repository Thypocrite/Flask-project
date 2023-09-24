from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'apple benanan key'


@app.route("/")
def index():
    return redirect(url_for("homepage"))


@app.route('/homepage')
def homepage():
    return render_template("homepage.html")


@app.route("/membersonly")
def membersonly():
    return render_template("membersonly.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        username = session["username"]
        return render_template("membersonly.html")
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
            login_message = "溫馨提示:用戶不存在,請先註冊"
            return render_template('login.html', message=login_message)
        else:
            if data[0] == password:
                session["username"] = username
                return redirect(url_for("membersonly"))
            else:
                login_message = "溫馨提示:密碼不正確,請確認"
                return render_template('login.html', message=login_message)

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        phonenumber = request.form["phonenumber"]
        birthday = request.form["birthday"]
        address = request.form["address"]
        email = request.form["email"]

        conn = sqlite3.connect("account.db")
        cursor = conn.cursor()
        sqlstr = "INSERT INTO members('username','password','email') values('" + \
            username+"','"+password+"','"+name+"','"+phonenumber + \
            "','"+birthday+"','"+address+"','"+email+"')"
        cursor.execute(sqlstr)
        conn.commit()
        sqlstr = "select password from members where username='"+username+"'"
        cursor.execute(sqlstr)
        data = cursor.fetchone()

        if data == None:
            login_message = "溫馨提示:註冊失敗"
            return render_template("register.html", message=login_message)
        else:
            return render_template("membersonly.html")
    else:
        return render_template("register.html")


def get_product_details(product_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('account.db')
    cursor = conn.cursor()

    # Query the database for the product details based on product_id
    sqlstr = "select name, price FROM goods WHERE product_id='"+product_id+"'"
    cursor.execute(sqlstr)
    product = cursor.fetchone()

    # Close the database connection
    conn.close()

    if product:
        # Return the product details as a dictionary
        return {'name': product[0], 'price': product[1]}
    else:
        return None


cart = []


@app.route('/add_to_cart', methods=["GET", "POST"])
def add_to_cart():
    product_id = request.form["product_id"]
    print(get_product_details(product_id))
    return product_id

    # product = get_product_details(product_id)

    # if product:
    #     # Add the product to the shopping cart
    #     cart.append(product)
    #     session['cart'] = cart  # Store the cart in the session
    # return redirect(url_for('homepage'))

# @app.route('/cart')
# def cart():
#     cart = session.get('cart', {})
#     total_price = sum(item['price'] * item['quantity']
#                       for item in cart.values())
#     return render_template('cart.html', cart=cart, total_price=total_price)


# @app.route('/remove_from_cart/<int:product_id>')
# def remove_from_cart(product_id):
#     cart = session.get('cart', {})
#     if product_id in cart:
#         del cart[product_id]
#         session['cart'] = cart
#     return redirect(url_for('cart'))


if __name__ == "__main__":
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
