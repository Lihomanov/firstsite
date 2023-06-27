from flask import Flask, request, jsonify, redirect, url_for
from flask import render_template
import sqlite3
from flask import send_file
from sqlite3 import Error
import random

n = 1

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


app = Flask(__name__)


@app.route('/')
@app.route('/main/')
def main():
    return render_template('main.html')


@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')


@app.route('/get_models', methods=['POST'])
def get_models():
    print("hhh")
    brand = request.json['brand']

    conn = create_connection("db_for_server")
    cursor = conn.cursor()

    # Выполнение запроса для получения моделей для выбранного бренда
    cursor.execute("SELECT DISTINCT model FROM Smartphone WHERE name_company = ?", (brand,))
    models = cursor.fetchall()

    # Закрытие соединения с базой данных
    conn.close()

    return jsonify(models)


@app.route('/next_id/<int:current_id>')
def get_next_id(current_id):
    conn = create_connection("db_for_server")
    cursor = conn.cursor()

    if (current_id == 0):
        cursor.execute('SELECT MIN(order_id) FROM Orders where order_id > (SELECT MIN(order_id) FROM Orders)')
        tmp = cursor.fetchall()
        current_id = tmp[0][0]
        next_id = current_id
    else:
        # Find the next available id greater than current_id
        cursor.execute("SELECT MIN(order_id) FROM Orders WHERE order_id > ?", (current_id,))
        next_id = cursor.fetchone()[0]


    if next_id is None:
        next_id = current_id

    return jsonify({'next_id': next_id})


@app.route('/previous_id/<int:current_id>')
def get_previous_id(current_id):
    conn = create_connection("db_for_server")
    cursor = conn.cursor()

    if (current_id == 0):
        cursor.execute('SELECT MIN(order_id) FROM Orders')
        tmp = cursor.fetchall()
        current_id = tmp[0][0]

    # Find the previous available id less than current_id
    cursor.execute("SELECT MAX(order_id) FROM Orders WHERE order_id < ?", (current_id,))
    previous_id = cursor.fetchone()[0]

    if previous_id is None:
        previous_id = current_id

    return jsonify({'previous_id': previous_id})







@app.route('/last_order')
def last_order():
    conn = create_connection("db_for_server")
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM Orders WHERE order_id = (SELECT MAX(order_id) FROM Orders)")
    last_order = cursor.fetchone()
    if last_order:
        return jsonify({'order_id': last_order[0]})
    else:
        return jsonify({'order_id': None})

@app.route('/first_order')
def first_order():
    conn = create_connection("db_for_server")
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM Orders WHERE order_id = (SELECT MIN(order_id) FROM Orders)")
    first_order = cursor.fetchone()
    if first_order:
        return jsonify({'order_id': first_order[0]})
    else:
        return jsonify({'order_id': None})


@app.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = create_connection("db_for_server")
    cursor = conn.cursor()

    print("order_id", order_id)
    if (order_id == 0):
        cursor.execute("DELETE FROM Orders WHERE order_id = (SELECT MIN(order_id) FROM Orders)")
        conn.commit()

    # Удаление записи с заданным order_id из таблицы Orders
    cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order_id,))
    conn.commit()

    return jsonify({'success': True})

# @app.route('/get_orders', methods=['GET'])
# def paginateOrders():
#     global n
#     conn = sqlite3.connect("db_for_server")
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT EXISTS (Select * from Orders where order_id = ?)",(n+1))
#     if(cursor.fetchone()[0]):
#
#     # print(cursor.fetchall())
#         next_id = n+1
#     else:
#         next_id = 1
#     # cursor.execute("SELECT  FROM Orders where order_id > ?", (currentPage,))
#
#     return redirect(url_for('vvod_info', next_id=next_id))

@app.route('/vvod/', methods=['GET', 'POST'])
def vvod_info():
    next_id = int(request.args.get("id",0))
    print("next_id =", next_id)
    conn = create_connection("db_for_server")
    cursor = conn.cursor()

    if (next_id == 0):
        cursor.execute('SELECT MIN(order_id) FROM Orders')
        tmp = cursor.fetchall()
        next_id = tmp[0][0]


    # Выполнение запроса для получения рейтингов
    cursor.execute('SELECT DISTINCT rating FROM Orders')
    ratings = cursor.fetchall()



    cursor.execute('SELECT DISTINCT rating FROM Orders where Orders.order_id = ?', (next_id,))
    make_ord = cursor.fetchall()
    ratings.remove(make_ord[0])
    ratings.insert(0, make_ord[0])

    # Выполнение запроса для получения модели
    cursor.execute(
        'SELECT DISTINCT model FROM Smartphone left join Orders on Smartphone.name_smartphone = Orders.id_model where Smartphone.name_company = (SELECT name_company from Smartphone inner join Orders O on Smartphone.name_smartphone = O.id_model where O.order_id = ?)',
        (next_id,))
    model = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT model FROM Smartphone left join Orders on Smartphone.name_smartphone = Orders.id_model where Orders.order_id = ?',
        (next_id,))
    make_ord = cursor.fetchall()
    model.remove(make_ord[0])
    model.insert(0, make_ord[0])

    # print(model)

    # Выполнение запроса для получения бренда
    cursor.execute('SELECT DISTINCT name_company FROM Smartphone')
    name_company = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT name_company FROM Smartphone left join Orders on Smartphone.name_smartphone = Orders.id_model where Orders.order_id = ?',
        (next_id,))
    make_ord = cursor.fetchall()
    name_company.remove(make_ord[0])
    name_company.insert(0, make_ord[0])

    cursor.execute("SELECT DISTINCT model FROM Smartphone WHERE name_company = 'LG'")
    modelsLG = cursor.fetchall()

    # Выполнение запроса для получения форм оплаты
    cursor.execute('SELECT DISTINCT payment_form FROM Orders')
    payment_forms = cursor.fetchall()

    cursor.execute('SELECT DISTINCT payment_form FROM Orders where Orders.order_id = ?', (next_id,))
    make_sta = cursor.fetchall()
    payment_forms.remove(make_sta[0])
    payment_forms.insert(0, make_sta[0])

    # Выполнение запроса для получения адреса
    cursor.execute('SELECT DISTINCT address FROM Warehouse')
    address = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT address FROM Warehouse left join Orders on Warehouse.warehouse_id = Orders.address_id where Orders.order_id = ?',
        (next_id,))
    make_addr = cursor.fetchall()
    address.remove(make_addr[0])
    address.insert(0, make_addr[0])

    # Выполнение запроса для получения статуса заказа
    cursor.execute('SELECT DISTINCT description FROM Status')
    description2 = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT description FROM Status left join Orders on Status.status_id = Orders.id_status where Orders.order_id = ?',
        (next_id,))
    make_desc2 = cursor.fetchall()
    description2.remove(make_desc2[0])
    description2.insert(0, make_desc2[0])

    # Выполнение запроса для получения акций
    cursor.execute('SELECT DISTINCT description FROM Discount')
    description = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT description FROM Discount left join Orders on Discount.discount_id = Orders.id_discount where Orders.order_id = ?',
        (next_id,))
    make_desc = cursor.fetchall()
    description.remove(make_desc[0])
    description.insert(0, make_desc[0])

    # Выполнение запроса для получения пользователей
    cursor.execute('SELECT DISTINCT username FROM User')
    username = cursor.fetchall()

    cursor.execute(
        'SELECT DISTINCT username FROM User left join Orders on User.user_id = Orders.id_user where Orders.order_id = ?',
        (next_id,))
    make_user = cursor.fetchall()
    username.remove(make_user[0])
    username.insert(0, make_user[0])

    # Получение предыдущего значения отзыва из базы данных
    cursor.execute("SELECT id_reviews FROM Orders  where Orders.order_id = ?", (next_id,))
    previous_review = cursor.fetchone()
    if previous_review:
        review = previous_review[0]
    else:
        review = ""

        # Получение предыдущего значения даты из базы данных
    cursor.execute("SELECT order_date FROM Orders where Orders.order_id = ?", (next_id,))
    previous_order_date = cursor.fetchone()
    if previous_order_date:
        order_date = previous_order_date[0]
    else:
        order_date = ""

        # Получение предыдущего значения цены из базы данных
    cursor.execute("SELECT price FROM Orders where Orders.order_id = ?", (next_id,))
    price = cursor.fetchone()
    if price:
        price = price[0]
    else:
        price = ""

    if request.method == 'POST':
        # "SELECT id_model,id_user, order_date,payment_form,address_id,id_status,id_discount,price,rating,id_reviews,order_id FROM Orders WHERE order_id = ?",
        # (current_order_id,))

        temp = request.form.get('id_model')
        cursor.execute("SELECT name_smartphone FROM Smartphone WHERE model = ?", (temp,))
        results = cursor.fetchone()
        id_model = results[0]

        temp = request.form.get('address_id')
        cursor.execute("SELECT warehouse_id FROM Warehouse WHERE address = ?", (temp,))
        results = cursor.fetchone()
        address_id = results[0]

        temp = request.form.get('id_discount')
        print(temp)
        cursor.execute("SELECT discount_id FROM Discount WHERE description = ?", (temp,))
        results = cursor.fetchone()
        id_discount = results[0]

        temp = request.form.get('id_status')
        print(temp)
        cursor.execute("SELECT status_id FROM Status WHERE description = ?", (temp,))
        results = cursor.fetchone()
        id_status = results[0]

        temp = request.form.get('id_user')
        print(temp)
        cursor.execute("SELECT user_id FROM User WHERE username = ?", (temp,))
        results = cursor.fetchone()
        id_user = results[0]

        # id_model = request.form.get('id_model')
        # id_user = request.form.get('id_user')
        # id_discount = request.form.get('id_discount')
        id_reviews = request.form.get('id_reviews')
        price = request.form.get('price')
        rating = request.form.get('rating')
        order_date = request.form.get('order_date')
        payment_form = request.form.get('payment_form')
        # address_id = request.form.get('address_id')
        # id_status = request.form.get('id_status')
        order_id = request.form.get('order_id')

        # Вставка данных в таблицу Orders
        cursor.execute(
            "INSERT INTO Orders (id_model,id_user,order_date,payment_form,address_id, id_status, id_discount,price,rating,id_reviews,order_id) VALUES (?, ?, ?,?, ?, ?,?, ?, ?,?, ?)",
            (id_model, id_user, order_date, payment_form, address_id, id_status, id_discount, price, rating, id_reviews,
             order_id))
        conn.commit()

    # Закрытие соединения с базой данных
    conn.close()

    return render_template('Vvod.html', review=review, order_date=order_date, price=price, ratings=ratings,
                           payment_forms=payment_forms, address=address, description=description, description2=description2,
                           model=model, name_company=name_company, username=username, modelsLG=modelsLG)


@app.route('/create_sm/', methods=['GET', 'POST'])
def create_sm():
    if request.method == 'POST':
        model = request.form.get('model')
        name_company = request.form.get('name_company')
        color = request.form.get('color')
        os = request.form.get('os')
        price = request.form.get('price')

        # Создание подключения к базе данных
        conn = create_connection("db_for_server")
        cursor = conn.cursor()

        # Вставка данных пользователя в таблицу User
        cursor.execute("INSERT INTO Smartphone (model, name_company, color, os, price) VALUES (?, ?, ?, ?,?)",
                       (model, name_company, color, os, price))
        conn.commit()

        # Закрытие соединения с базой данных
        # conn.close()

    return render_template('create_sm.html')


@app.route('/new_user/', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        username = request.form.get('username')
        phone = request.form.get('phone')

        # Создание подключения к базе данных
        conn = create_connection("db_for_server")
        cursor = conn.cursor()

        # Вставка данных пользователя в таблицу User
        cursor.execute("INSERT INTO User (last_name, role, username, phone) VALUES (?, ?, ?, ?)",
                       (last_name, role, username, phone))
        conn.commit()

        # Закрытие соединения с базой данных
        # conn.close()

    return render_template('new_user.html')


@app.route('/dw/')
def dnwld():
    return send_file('db_for_server')





# @app.route('/get_payment_types', methods=['POST'])
# def get_payment_types():
#     selected_brand = request.json['brand']
#
#     conn = create_connection("db_for_server")
#     cursor = conn.cursor()
#
#     # Выполнение запроса для получения типов оплаты для выбранного бренда
#     cursor.execute("SELECT DISTINCT payment_form FROM Orders WHERE id_model = ?", (selected_brand,))
#     payment_types = cursor.fetchall()
#
#     # Закрытие соединения с базой данных
#     conn.close()
#
#     return jsonify(payment_types)
#
#
# @app.route('/get_order_statuses', methods=['POST'])
# def get_order_statuses():
#     conn = create_connection("db_for_server")
#     cursor = conn.cursor()
#     selected_payment_type = request.json['payment_type']
#     if selected_payment_type in order_statuses:
#         return jsonify(order_statuses[selected_payment_type])
#     else:
#         return jsonify([])





@app.route('/search/', methods=['GET', 'POST'])
def search():

    context = ""
    loli = []
    conn = create_connection("db_for_server")
    conn = conn.cursor()

    conn.execute('SELECT DISTINCT name_company FROM Smartphone')
    options = conn.fetchall()
    options.insert(0, (''))

    conn.execute('SELECT DISTINCT payment_form FROM Orders')
    options1 = conn.fetchall()
    options1.insert(0, (''))

    conn.execute('SELECT DISTINCT name_status FROM Status')
    options2 = conn.fetchall()
    options2.insert(0, (''))

    brand = "LG"
    conn.execute("SELECT * FROM Orders WHERE id_model = ?", (brand,))
    results = conn.fetchall()

    models = request.args.get('my_dropdown')
    payments_type = request.args.get('type')
    status = request.args.get('type1')
    print(models, payments_type, status)
    print(type(models))
    if ((models == None and payments_type == None and status == None) or (
            models == "" and payments_type == "" and status == "")):
        print(1111)
        sqlite_select_query = """SELECT Smartphone.model,
               Smartphone.name_company, 
               User.username,
               Orders.order_date,
               Orders.payment_form,
               Warehouse.address,
               Status.name_status,
               Discount.discount_name,
               Orders.price,
               Orders.rating,
               Orders.id_reviews
                from Orders
                inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                inner join Discount on Orders.id_discount = Discount.discount_id
                inner join Status on Orders.id_status = Status.status_id
                inner join User on Orders.id_user = User.user_id"""

    elif ((models != None and payments_type == None and status == None) or (
            models != "" and payments_type == "" and status == "")):
        print(2222)
        sqlite_select_query = """SELECT Smartphone.name_company,
               Smartphone.model,
               User.username,
               Orders.order_date,
               Orders.payment_form,
               Warehouse.address,
               Status.name_status,
               Discount.discount_name,
               Orders.price,
               Orders.rating,
               Orders.id_reviews
                from Orders
                inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                inner join Discount on Orders.id_discount = Discount.discount_id
                inner join Status on Orders.id_status = Status.status_id
                inner join User on Orders.id_user = User.user_id
                where Smartphone.name_company = '%s' """ % models
    elif ((models == None and payments_type != None and status == None) or (
            models == "" and payments_type != "" and status == "")):
        print(333)
        sqlite_select_query = """SELECT Smartphone.name_company,
                       Smartphone.model,
                       User.username,
                       Orders.order_date,
                       Orders.payment_form,
                       Warehouse.address,
                       Status.name_status,
                       Discount.discount_name,
                       Orders.price,
                       Orders.rating,
                       Orders.id_reviews
                        from Orders
                        inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                        inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                        inner join Discount on Orders.id_discount = Discount.discount_id
                        inner join Status on Orders.id_status = Status.status_id
                        inner join User on Orders.id_user = User.user_id
                        where  Orders.payment_form = '%s' """ % payments_type

    elif ((models == None and payments_type == None and status != None) or (
            models == "" and payments_type == "" and status != "")):
        print(4444)
        sqlite_select_query = """SELECT Smartphone.name_company,
                               Smartphone.model,
                               User.username,
                               Orders.order_date,
                               Orders.payment_form,
                               Warehouse.address,
                               Status.name_status,
                               Discount.discount_name,
                               Orders.price,
                               Orders.rating,
                               Orders.id_reviews
                                from Orders
                                inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                                inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                                inner join Discount on Orders.id_discount = Discount.discount_id
                                inner join Status on Orders.id_status = Status.status_id
                                inner join User on Orders.id_user = User.user_id
                                where  Status.name_status = '%s' """ % status

    elif ((models != None and payments_type != None and status == None) or (
            models != "" and payments_type != "" and status == "")):
        print(5555)
        sqlite_select_query = """SELECT Smartphone.name_company,
                                       Smartphone.model,
                                       User.username,
                                       Orders.order_date,
                                       Orders.payment_form,
                                       Warehouse.address,
                                       Status.name_status,
                                       Discount.discount_name,
                                       Orders.price,
                                       Orders.rating,
                                       Orders.id_reviews
                                        from Orders
                                        inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                                        inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                                        inner join Discount on Orders.id_discount = Discount.discount_id
                                        inner join Status on Orders.id_status = Status.status_id
                                        inner join User on Orders.id_user = User.user_id
                                        where  Smartphone.name_company = '%s' and Orders.payment_form  = '%s' """ % (
        models, payments_type)

    elif ((models != None and payments_type == None and status != None) or (
            models != "" and payments_type == "" and status != "")):
        print(6666)
        sqlite_select_query = """SELECT Smartphone.name_company,
                                               Smartphone.model,
                                               User.username,
                                               Orders.order_date,
                                               Orders.payment_form,
                                               Warehouse.address,
                                               Status.name_status,
                                               Discount.discount_name,
                                               Orders.price,
                                               Orders.rating,
                                               Orders.id_reviews
                                                from Orders
                                                inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                                                inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                                                inner join Discount on Orders.id_discount = Discount.discount_id
                                                inner join Status on Orders.id_status = Status.status_id
                                                inner join User on Orders.id_user = User.user_id
                                                where  Smartphone.name_company = '%s' and Status.name_status = '%s' """ % (
        models, status)

    elif ((models == None and payments_type != None and status != None) or (
            models == "" and payments_type != "" and status != "")):
        print(7777)
        sqlite_select_query = """ SELECT Smartphone.name_company,
                                                       Smartphone.model,
                                                       User.username,
                                                       Orders.order_date,
                                                       Orders.payment_form,
                                                       Warehouse.address,
                                                       Status.name_status,
                                                       Discount.discount_name,
                                                       Orders.price,
                                                       Orders.rating,
                                                       Orders.id_reviews
                                                        from Orders
                                                        inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                                                        inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                                                        inner join Discount on Orders.id_discount = Discount.discount_id
                                                        inner join Status on Orders.id_status = Status.status_id
                                                        inner join User on Orders.id_user = User.user_id
                                                        where  Orders.payment_form = '%s' and Status.name_status = '%s' """ % (
        payments_type, status)

    else:
        print(8888)
        sqlite_select_query = """SELECT Smartphone.name_company,
                                                              Smartphone.model,
                                                              User.username,
                                                              Orders.order_date,
                                                              Orders.payment_form,
                                                              Warehouse.address,
                                                              Status.name_status,
                                                              Discount.discount_name,
                                                              Orders.price,
                                                              Orders.rating,
                                                              Orders.id_reviews
                                                               from Orders
                                                               inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                                                               inner join Warehouse on Orders.address_id = Warehouse.warehouse_id
                                                               inner join Discount on Orders.id_discount = Discount.discount_id
                                                               inner join Status on Orders.id_status = Status.status_id
                                                               inner join User on Orders.id_user = User.user_id
                                                               where Orders.payment_form = '%s' and  Status.name_status = '%s' and  Smartphone.name_company = '%s' """ % (
        payments_type, status, models)

    conn.execute(sqlite_select_query)
    records = conn.fetchall()
    print(records)
    for i, row in enumerate(records):
        loli.append([])
        loli[i].append(i + 1)
        for f, j in enumerate(row):
            loli[i].append(j)
    conn.close()

    return render_template('search.html', context=loli, options=options, options1=options1, options2=options2,
                           results=results)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/statistic/')
def statistic():
    conn = create_connection("db_for_server")
    conn = conn.cursor()
    loli = []
    sql_req = """SELECT Smartphone.name_company, Count(Smartphone.name_company) as cnt
                        from Orders
                        inner join Smartphone on Orders.id_model = Smartphone.name_smartphone
                        group by  Smartphone.name_company"""
    conn.execute(sql_req)
    records = conn.fetchall()
    values = []
    labels = []
    colors = []
    loli = []
    for i, x in enumerate(records):
        print(x[0], x[1])
        loli.append([])
        loli[i].append(x[0])
        loli[i].append(x[1])
        r = lambda: random.randint(0, 255)
        colors.append('#%02X%02X%02X' % (r(), r(), r()))
        labels.append(x[0])
        values.append(int(x[1]))

    conn.close()

    return render_template('statistic.html', context=loli, max=sum(values), set=zip(values, labels, colors))


@app.route('/vigryzka file database/')
def vigryzka():
    return render_template('vigryzka file database.html')


@app.errorhandler(404)
def n_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run()