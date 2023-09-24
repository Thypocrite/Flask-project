from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3


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
    sqlstr = "select product_id name, price FROM goods WHERE product_id='"+product_id+"'"
    cursor.execute(sqlstr)
    product = cursor.fetchone()

    # Close the database connection
    conn.close()

    if product:
        # Return the product details as a dictionary
        return {'name': product[0], 'price': product[1]}
    else:
        return None


@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    product_id = request.form.get('product_id')
    # Fetch the product details based on product_id (you can use your existing get_product_details function)
    product_details = get_product_details(product_id)

    if product_details:
        # Check if a cart exists in the session, and initialize an empty cart if not
        if 'cart' not in session:
            session['cart'] = []
        # Add the selected product to the cart
        product_details['product_id'] = product_id
        session['cart'].append(product_details)
        return redirect('/homepage')  # Redirect back to the product page
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
