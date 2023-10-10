from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
import time
import re
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate


app = Flask(__name__)
app.secret_key = 'apple benanan key'


@app.route("/")  # 根目錄
def index():
    return redirect(url_for("homepage"))


@app.errorhandler(404)  # 找不到網頁
def pageNotFound(error):
    return render_template("PageNotFound.html"), 404


@app.route('/homepage')  # 首頁
def homepage():
    if "user" not in session:
        user_id = "w@q"
    else:
        user_id = session['user']

    top_recommendations = get_top_n_recommendations(user_id, n=4)
    recommendations = [tuple(row) for row in top_recommendations.values]

    products = [(6529468, '【PS5】胡鬧廚房！全都好吃 (原譯：煮過頭 吃到飽)《中文版》', 'NT$880', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6529468/0/637973753679270000?v=1'), (6529560, '【PS5】惡魔靈魂 重製版《中文版》', 'NT$1,590', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6529560/0/638229724827600000?v=1'), (6529581, '【PS5】跑車浪漫旅 7 (GT7)《中文版》', 'NT$1,990', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6529581/0/638222480068400000?v=1'), (6529660, '【PS5】鬼線：東京 GhostWire:Tokyo《中文版》', 'NT$1,790', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6529660/0/638282413571300000?v=1'), (6542048, '【PS5】死亡回歸 Returnal《中文版》', 'NT$1,590', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6542048/0/638282366902300000?v=1'), (6542178, '【PS5】小小大冒險《中文版》', 'NT$1,790', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6542178/0/638260616442070000?v=1'),
                (6571086, '【PS5】惡魔獵人 5 特別版《中文版》', 'NT$1,190', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6571086/0/637903759896270000?v=1'), (6600410, '【PS5】魔法氣泡™ 特趣思™ 俄羅斯方塊™ 2《中文版》', 'NT$1,290', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6600410/0/638258139715200000?v=1'), (6615536, '【PS5】漫威蜘蛛人：邁爾斯摩拉斯 終極版《中文版》', 'NT$1,990', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6615536/0/638291232246100000?v=1'), (6637292, '【PS5】真人快打 11 終極版《簡體中文版》', 'NT$699', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6637292/0/638223481859970000?v=1'), (6755107, '【PS5】仁王 收藏輯《中文版》', 'NT$1,590', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6755107/0/638273600726770000?v=1'), (6773543, '【PS5】人中之龍 7 光與闇的去向 國際版《中文版》', 'NT$1,490', '//diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/6773543/0/638260616775730000?v=1')]
    return render_template("homepage.html", products=products, recommendations=recommendations)


@app.route('/category/<category_name>', methods=["GET", "POST"])  # 商品分類頁
def category(category_name):
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE title LIKE ?", ('%' + category_name + '%',))
    products = cursor.fetchall()
    row_count = len(products)
    conn.close()
    if products:
        return render_template("category.html", products=products, row_count=row_count, category_name=category_name)
    else:
        return render_template("PageNotFound.html"), 404


@app.route('/salePage/<int:product_id>', methods=["GET", "POST"])  # 商品單項頁
def salePage(product_id):
    single_product = get_product_details(str(product_id))
    description_head = single_product[6].split()[0]
    description_body = " ".join(single_product[6].split()[1:])
    if single_product:
        return render_template("salePage.html", single_product=single_product, description_head=description_head, description_body=description_body)
    else:
        return render_template("PageNotFound.html"), 404


@app.route('/search', methods=["GET"])  # 查詢功能
def search():
    keyword = request.args.get('keyword')
    conn = sqlite3.connect("merged.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE title LIKE ?",
                   ('%'+keyword+'%',))
    products = cursor.fetchall()
    conn.close()

    if keyword == "":
        products = None

    if products:
        row_count = len(products)
    else:
        row_count = 0

    return render_template("search.html", products=products, row_count=row_count, keyword=keyword)


@app.route('/membersonly/data')  # 會員-會員資料
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


@app.route('/login', methods=['POST', 'GET'])  # 會員-登入
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


@app.route("/logout")  # 會員-登出
def logout():
    session.pop("user", None)
    return render_template("login.html")


@app.route('/reg', methods=['POST', 'GET'])  # 會員-註冊
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


@app.route('/changePassword', methods=['POST', 'GET'])  # 會員-重設密碼
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


@app.route('/purchasehistory')  # 會員-購買紀錄
def purchasehistory():
    if 'user' in session:
        user = session['user']
        connection = sqlite3.connect('merged.db')
        cur = connection.cursor().execute(
            "select * from totall where user='"+user+"'")
        rows = cur.fetchall()

        return render_template('purchasehistory.html', rows=rows)
    else:
        return render_template('login.html')


@app.route('/administrationuser', methods=['POST', 'GET'])  # 管理區-會員資料
def administrationuser():
    connection = sqlite3.connect('merged.db')
    cur = connection.cursor().execute("select * from lccnet")
    rows = cur.fetchall()
    return render_template('administrationuser.html', rows=rows)


@app.route('/datam', methods=['POST'])  # 管理區-會員資料修改
def datam():
    user = request.form.get("user")
    passwd = request.form['passwd']
    name = request.form['name']
    pho = request.form['pho']
    bir = request.form['bir']
    addr = request.form['addr']
    connection = sqlite3.connect('merged.db')
    cursor = connection.cursor()

    sql_query = """
    UPDATE lccnet SET
        passwd = CASE WHEN ? <> '' THEN ? ELSE passwd END,
        name = CASE WHEN ? <> '' THEN ? ELSE name END,
        phonenumber = CASE WHEN ? <> '' THEN ? ELSE phonenumber END,
        birthday = CASE WHEN ? <> '' THEN ? ELSE birthday END,
        address = CASE WHEN ? <> '' THEN ? ELSE address END

    WHERE user= ?"""
    cursor.execute(sql_query, (passwd, passwd, name,
                   name, pho, pho, bir, bir, addr, addr, user))

    cursor = connection.cursor().execute("select * from lccnet")
    rows = cursor.fetchall()
    connection.commit()
    connection.close()
    return render_template('administrationuser.html', rows=rows)


@app.route('/dataSearch', methods=['POST', 'GET'])  # 管理區-會員資料修改-搜尋
def dataSearch():

    member = request.form.get("member")
    connection = sqlite3.connect('merged.db')
    cur = connection.cursor().execute(
        "select * from lccnet where user='"+member+"'")
    records = cur.fetchone()

    if records:
        return render_template('datamodification.html', records=records)
    else:
        flash("請輸入正確的帳號名稱!", "error")
        return redirect(request.referrer)


@app.route('/order', methods=['POST', 'GET'])  # 管理區-訂單紀錄
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


@app.route('/administrator', methods=['POST', 'GET'])  # 管理區-管理員新增
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


def get_product_details(product_id):  # 查找商品資料
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


@app.route('/add_to_cart', methods=["POST"])  # 加入購物車
def add_to_cart():
    if 'user' not in session:
        flash('請先登入您的帳戶!', 'error')
        return redirect(request.referrer)

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

        flash(f'商品{title}已成功加入購物車!', 'success')
    else:
        flash('商品已在您的購物車中!', 'error')

    return redirect(request.referrer)


@app.route('/cart')  # 購物車內容
def cart():
    if 'user' not in session:
        flash('請先登入您的帳戶!', 'error')
        return redirect(request.referrer)
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


@app.route('/remove_from_cart', methods=['POST'])  # 移除購物車中指定商品
def remove_from_cart():
    if 'user' not in session:
        flash('請先登入您的帳戶!', 'error')
        return redirect(request.referrer)

    product_id = request.form.get('product_id')
    user = session['user']

    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title From carts WHERE user= ? and salePageId= ?", (user, str(product_id)))
    in_cart = cursor.fetchone()

    if in_cart:
        cursor.execute(
            "DELETE FROM carts WHERE user= ? and salePageId= ?", (user, str(product_id)))
        conn.commit()
        conn.close()
    # Extract the text between two single quotes from tuple "in_cart"
    title = in_cart[0].strip("'")
    flash(f'商品{title}已移出購物車!', 'error')
    return redirect('/cart')  # Redirect back to the cart page after removal


@app.route('/checkout', methods=['POST'])  # 結帳
def checkout():
    if 'user' not in session:
        flash('請先登入您的帳戶!', 'error')
        return redirect(request.referrer)

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
        flash('感謝您的消費!', 'success')
        return render_template('checkout.html', cart_items=cart_items, total_price=total_price, order_id=order_id, order_date=order_date)
    else:
        flash('您的購物車目前沒有商品!', 'error')
        return redirect(request.referrer)


@app.route('/clear_cart')  # 清除購物車中所有商品
def clear_cart():
    if 'user' not in session:
        flash('請先登入您的帳戶!', 'error')
        return redirect(request.referrer)

    user = session['user']
    conn = sqlite3.connect('merged.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carts Where user='"+user+"'")
    conn.commit()
    conn.close()

    flash('已清空您的購物車!', 'success')
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
                        'div', class_='sc-kKQOHL hjKVxV')

                    if title_element:
                        title = title_element.text.strip()
               # 如果商品在資料庫中已經存在，從 existing_products 中移除
                        if title in existing_products:
                            existing_products.remove(title)
                        else:
                            price_element = product_element.find(
                                'div', class_='sc-gIeZgt hEqCsd')
                            image_element = product_element.find(
                                'img', class_='product-card__vertical__media product-card__vertical__media-tall')
                            link_element = product_element.find(
                                'a', class_='sc-hQlIKd jnYvQx product-card__vertical product-card__vertical--hover new-product-card')

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

# 這裡我們返回一個JSON響應，表明操作成功
        flash("成功更新商品")
        return redirect(url_for('productsonshelves'))

    else:
        return render_template('productsonshelves.html')


def get_top_n_recommendations(user_id, n=4):
    # 连接到SQLite数据库
    conn = sqlite3.connect('merged.db')
    members = pd.read_sql_query('SELECT * FROM lccnet', conn)
    products = pd.read_sql_query('SELECT * FROM products', conn)
    purchases = pd.read_sql_query('SELECT * FROM totall', conn)
    conn.close()
    # 计算年龄并进行分组
    CURRENT_YEAR = 2023
    members['age'] = CURRENT_YEAR - \
        pd.to_datetime(members['birthday'], format='%Y-%m-%d').dt.year
    bins = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100]
    labels = ['15-19', '20-24', '25-29', '30-34', '35-39',
              '40-44', '45-49', '50-54', '55-59', '60+']
    members['age_group'] = pd.cut(
        members['age'], bins=bins, labels=labels, right=False)

    # 将购买历史和用户年龄组合在一起
    purchases = purchases.merge(members[['user', 'age_group']], on='user')

    # 模拟"评分"列，你可以根据需要替换这个逻辑
    purchases['purchase_dummy'] = 1

    # 使用协同过滤模型
    reader = Reader(rating_scale=(0, 1))  # 我们的评分列是购买/未购买
    data = Dataset.load_from_df(
        purchases[['user', 'salePageId', 'purchase_dummy']], reader)

    # 使用SVD模型
    model = SVD()
    cross_validate(model, data, measures=['RMSE'], cv=5, verbose=True)

    # 训练模型
    trainset = data.build_full_trainset()
    model.fit(trainset)

    # 函数来获取推荐
    # 获取用户还未购买过的商品
    all_products = products['salePageId'].unique()
    purchased_products = purchases[purchases['user']
                                   == user_id]['salePageId'].unique()
    not_purchased_products = set(all_products) - set(purchased_products)

    # 预测用户对未购买商品的评分
    predictions = []
    for product_id in not_purchased_products:
        predictions.append(
            (product_id, model.predict(user_id, product_id).est))

    # 获取评分最高的前n个商品
    top_n_product_ids = [x[0] for x in sorted(
        predictions, key=lambda x: x[1], reverse=True)[:n]]

    # 获取这些商品的详细信息
    top_n_products = products[products['salePageId'].isin(
        top_n_product_ids)][['salePageId', 'title', 'price', 'image_url']]

    return top_n_products


if __name__ == "__main__":
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
