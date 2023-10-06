from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
import time
import re


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


@app.route('/salePage/<int:product_id>', methods=["GET", "POST"])
def salePage(product_id):
    single_product = get_product_details(str(product_id))
    return render_template("salePage.html", single_product=single_product)


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
    sqlstr = "select * FROM products WHERE salePageId='"+product_id+"'"
    cursor.execute(sqlstr)
    product = cursor.fetchone()
    # Close the database connection
    conn.close()

    if product:
        return product
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

            salePageId = str(product_details[0])
            title = product_details[1]
            price = product_details[2]
            image_url = product_details[3]
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


# 管理區-商品上架
@app.route('/productsonshelves', methods=['POST', 'GET'])
def productsonshelves():
    if request.method == 'POST':
        conn = sqlite3.connect('merged.db')
        cur = conn.cursor()

# 建立名為 "products" 的資料表
        cur.execute('''CREATE TABLE IF NOT EXISTS products
                        (salePageId INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        price TEXT,
                        image_url TEXT,
                        link_url TEXT,
                        first_description TEXT,
                        second_description TEXT)''')


# 创建图像链接表
        cur.execute('''
            CREATE TABLE IF NOT EXISTS image_urls (
            salePageId TEXT,
            url TEXT
            )
        ''')
# 使用 Selenium 開啟網頁

        urls = [
            'https://www.tvgame.com.tw/v2/official/SalePageCategory/353560?sortMode=Curator',
            'https://www.tvgame.com.tw/v2/official/SalePageCategory/494728?sortMode=Curator'
        ]

# 查詢資料庫以獲取已經存在的商品
        cur.execute("SELECT title FROM products")

        existing_products = [row[0] for row in cur.fetchall()]

# 创建一个名为 "products" 的表格


# 遍歷每個URL
        for url in urls:
           # 使用 Selenium 開啟網頁
            driver = webdriver.Chrome()
            driver.get(url)


# 使用 Selenium 等待網頁載入完成（根據實際情況調整等待時間）
            time.sleep(5)

    # 獲取網頁內容
            html_content = driver.page_source

    # 關閉網頁
            driver.quit()

    # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(html_content, 'html.parser')

    # 找到包含商品信息的HTML元素
            product_elements = soup.find_all(
                'li', class_='column-grid-container__column')

            first_description = "未提供商品描述"
            second_description = "未提供商品描述"
            additional_info_div = None  # 用于存储附加信息的<div>
            image_urls = []  # 用于存储图片URL的列表

            if product_elements:
                for product_element in product_elements:
                    # 從每個商品元素中提取標題
                    title_element = product_element.find(
                        'div', class_='sc-ALVnD jttWOh')

                    if title_element:
                        title = title_element.text.strip()
               # 如果商品在資料庫中已經存在，從 existing_products 中移除
                        if title in existing_products:
                            existing_products.remove(title)
                        else:
                            price_element = product_element.find(
                                'div', class_='sc-KzItE gRTtOW')
                            image_element = product_element.find(
                                'img', class_='product-card__vertical__media product-card__vertical__media-tall')
                            link_element = product_element.find(
                                'a', class_='sc-bSGrXo dvnSEx product-card__vertical product-card__vertical--hover new-product-card')

                            if price_element and image_element and link_element:
                                price = price_element.text.strip()
                                image_url = image_element['src']
                                link_url = 'https://www.tvgame.com.tw' + \
                                    link_element['href']
                                salePageId = link_url.split('/')[-1]

                        # 插入新的商品信息到資料庫中
                        # cur.execute("INSERT INTO products (title, price, image_url, link_url) VALUES (?, ?, ?, ?)",
                        #             (title, price, image_url, link_url))
                        # conn.commit()

                        # 輸出提取的商品信息
                                print(f'標題: {title}')
                                print(f'價格: {price}')
                                print(f'圖片 URL: {image_url}')
                                print(f'連結 URL: {link_url}')

                        # 進入商品詳細頁面
                                driver = webdriver.Chrome()
                                driver.get(link_url)

                        # 在商品詳細頁面上進行更多信息提取
                        # 這裡可以添加代碼来提取更多细信息
                        # 使用 Selenium 等待商品詳細頁面載入完成（根據實際情況調整等待時間）
                                time.sleep(5)

                                page_source = driver.page_source
                                soup = BeautifulSoup(
                                    page_source, 'html.parser')

                                product_info = soup.find(
                                    "div", class_="right-sub-content")

                                first_description = "未提供商品描述"
                                second_description = "未提供商品描述"
                                additional_info_div = None  # 用于存储附加信息的<div>
                                image_urls = []  # 用于存储图片URL的列表

                                if product_info:
                                    # 查找包含商品描述的HTML元素，这里假设商品描述位于一个<p>元素中
                                    product_description_span = product_info.find(
                                        "div", class_="salepage-detail-info")

                                    if product_description_span:
                                        product_description = product_description_span.text.strip()

                                # 删除特定文本
                                        specific_text = "※無法指定收貨時間，有特殊需求請先至客服詢問 (訂單備註非問答區)※如遇原廠貨量不足/取消生產/調整價格/延遲出貨，將於收到原廠發布消息後以簡訊通知取消訂單/重新下單。(請定時確認帳號電話號碼正確&暢通，若設定不接收商務簡訊導致未收到通知請自行至商品頁或客服留言確認資訊)※請於上市前檢查取貨門市是否閉店、閉店將無法出貨。重選後也請於客服留言告知可出貨。"
                                        product_description = product_description.replace(
                                            specific_text, "")
                                        first_description = specific_text
                                        second_description = product_description

                             # 在<div>元素中查找<img>元素
                                    img_elements = product_info.find_all("img")

                                    if img_elements:
                                        # 提取<img>元素的src属性，即图片的URL
                                        for img_element in img_elements:
                                            image_url2 = img_element.get("src")
                                            if image_url2:
                                                image_urls.append(image_url2)

                         # 将数据插入产品表
                                cur.execute('''
                                        INSERT INTO products (salePageId, title, price, image_url, link_url, first_description, second_description)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    ''', (salePageId, title, price, image_url, link_url, first_description, second_description))

                        # 将图像链接插入图像链接表
                                for url in image_urls:
                                    if "webapi/images/r/SalePageDesc" in url:
                                        cur.execute('''
                                            INSERT INTO image_urls (salePageId, url)
                                            VALUES (?, ?)
                                        ''', (salePageId, url))

                                conn.commit()

                                print(f'標題: {title}')
                                print(f'價格: {price}')
                                print(f'圖片 URL: {image_url}')
                                print(f'連結 URL: {link_url}')
                                print(f"商品描述: {product_description}")
                                print(f"第一段商品描述: {first_description}")
                                print(f"第二段商品描述: {second_description}")
                                for url in image_urls:
                                    if "webapi/images/r/SalePageDesc" in url:
                                        print(f"销售页面图像链接: {url}")
                        # 詳關閉商品詳細頁面
                                driver.quit()


# 刪除不再存在於網站上的商品記錄
        if existing_products:
            for product_title in existing_products:
                cur.execute("DELETE FROM products WHERE title=?",
                            (product_title,))
            conn.commit()

# 關閉資料庫連接
        conn.close()

    else:
        return render_template('productsonshelves.html')


if __name__ == "__main__":
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
