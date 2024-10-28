from flask import Flask, json, make_response, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
from hashlib import sha1
from datetime import datetime, timedelta

app = Flask(__name__)

app.config.update(
    MYSQL_HOST='localhost',
    MYSQL_USER='root',
    MYSQL_PASSWORD='',
    MYSQL_DB='cadastrodb',
    MYSQL_CURSORCLASS='DictCursor',
    MYSQL_CHARSET='utf8mb4',
    MYSQL_USE_UNICODE=True
)

mysql = MySQL(app)


@app.before_request
def before_request():
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")
    cur.execute("SET character_set_client=utf8mb4")
    cur.execute("SET character_set_results=utf8mb4")
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()


@app.route('/')
def home():

    cookie = request.cookies.get('user')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user_id = '1'

    sql = '''
        SELECT *
        FROM item
        WHERE
            it_owner = %s
            AND it_status != 'del'
        ORDER BY it_date DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user_id, ))
    itens = cur.fetchall()
    cur.close()

    page = {
        "title": 'Página Inicial',
        "itens": itens
    }
    return render_template('home.html', page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        form = dict(request.form)

        sql = '''
            SELECT ow_id, ow_name
            FROM owner
            WHERE ow_email = %s
                AND ow_password = SHA1(%s)
                AND ow_status = 'on'
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], form['password'],))
        user = cur.fetchone()
        cur.close()

        if user != None:

            resp = make_response(redirect(url_for('home')))

            cookie_data = {
                'id': user['ow_id'],
                'name': user['ow_name']
            }
            # Data em que o cookie expira
            expires = datetime.now() + timedelta(days=365)
            # Adicona o cookie à página
            resp.set_cookie('user_data', json.dumps(
                cookie_data), expires=expires)

            return resp
        else:
            error = 'Login e/ou senha errados!'

    page = {
        "css": 'login.css',
        "title": "Página de Login"
    }

    return render_template('login.html', page=page)


@app.route('/newOwner', methods=['GET', 'POST'])
def new_owner():
    if request.method == 'POST':
        form = dict(request.form)

    page = {
        'title': 'Novo Proprietário',
        'css': 'new_owner.css'
    }
    return render_template('new_owner.html', page=page)


@app.route('/newItem', methods=['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        form = dict(request.form)

    page = {
        'title': 'Novo Item',
        'css': 'new_item.css'
    }
    return render_template('new_item.html', page=page)


if __name__ == '__main__':
    app.run(debug=True)
