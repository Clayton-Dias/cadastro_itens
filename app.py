from flask import Flask, json, make_response, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
from hashlib import sha1
from datetime import datetime, timedelta
import subprocess
import random
import string

app = Flask(__name__)

# Configuração do MySQL
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


def send_email(email_to, subject, content):
    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = "" # API KEY gerado no sendgrid.
    email_from = "" # Email autenticado no sendgrid.

    payload = {
        "personalizations": [{
            "to": [{
                "email": email_to
            }]
        }],
        "from": {
            "email": email_from
        },
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": content
        }]
    }

    result = subprocess.run([
        "curl",
        "--request", "POST",
        "--url", url,
        "--header", f"Authorization: Bearer {api_key}",
        "--header", "Content-Type: application/json",
        "--data", json.dumps(payload)
    ], capture_output=True, text=True)

    return result.stdout, result.stderr

def get_new_password(tamanho=8):
    caracteres = string.ascii_letters + string.digits + "_-$&"
    return ''.join(random.choice(caracteres) for _ in range(tamanho))



@app.before_request
def before_request():
    """Configurações de codificação para garantir o suporte a UTF-8."""
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")
    cur.execute("SET character_set_client=utf8mb4")
    cur.execute("SET character_set_results=utf8mb4")
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()

# Rota principal do aplicativo, exibe a página inicial com itens do usuário.


@app.route('/')
def home():

    edit = request.args.get('edit')
    delete = request.args.get('delete')

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT *
        FROM item
        WHERE
            it_owner = %s
            AND it_status != 'del'
        ORDER BY it_date DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], ))
    things = cur.fetchall()
    cur.close()

    # Renderiza a página inicial com os itens do usuário
    return render_template('home.html', things=things, user=user, edit=edit, delete=delete)


# Rota de login para autenticação de usuários
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = ''

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
            # Criação de um cookie de sessão para o usuário autenticado
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

    return render_template('login.html', error=error)


@app.route('/new', methods=['GET', 'POST'])
def new_item():
    success = False

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    if request.method == 'POST':
        form = dict(request.form)

        sql = '''
            INSERT INTO item (
                it_owner, it_image, it_name, it_description, it_location
            ) VALUES (
                %s, %s, %s, %s, %s
            )
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (user['id'], form['image'],
                    form['name'], form['description'], form['location']))
        mysql.connection.commit()
        cur.close()

        success = True

    return render_template('new_item.html', user=user, success=success)


@app.route('/view/<id>')
def view(id):

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT it_id, it_date, it_image, it_name, it_description, it_location
        FROM item
        WHERE it_status = 'on' AND it_owner = %s AND it_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    thing = cur.fetchone()
    cur.close()

    return render_template('view.html', user=user, thing=thing)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(url_for('login'))

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    if request.method == 'POST':

        form = dict(request.form)

        sql = '''
            UPDATE item SET 
                it_image = %s,
                it_name = %s,
                it_description = %s,
                it_location = %s
            WHERE it_status = 'on'
                AND it_owner = %s
                AND it_id = %s
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['image'], form['name'],
                    form['description'], form['location'], user['id'], id,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home', edit=True))

    sql = '''
        SELECT it_id, it_date, it_image, it_name, it_description, it_location
        FROM item
        WHERE it_status = 'on' AND it_owner = %s AND it_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    thing = cur.fetchone()
    cur.close()

    return render_template('edit.html', user=user, thing=thing)


@app.route('/delete/<id>')
def delete(id):

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(url_for('login'))

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        UPDATE item SET
            it_status = 'del'
        WHERE it_owner = %s
            AND it_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home', delete=True))


@app.route('/logout')
def logout():

    resp = make_response(redirect(url_for('login')))

    resp.set_cookie('user_data', '', expires=0)

    return resp


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():

    cookie = request.cookies.get('user_data')
    if cookie != None:
        return redirect(url_for('home'))

    feedback = ''
    form = {}

    if request.method == 'POST':

        form = dict(request.form)

        sql = '''
            SELECT count(ow_id) AS total
            FROM owner
            WHERE ow_email = %s
                AND ow_status != 'del'
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], ))
        total = int(cur.fetchone()['total'])
        cur.close()

        if total == 0:
            sql = '''
                INSERT INTO owner (ow_birth, ow_name, ow_email, ow_password)
                VALUES (%s, %s, %s, SHA1(%s))
            '''
            cur = mysql.connection.cursor()
            cur.execute(sql, (form['birth'], form['name'],
                        form['email'], form['password'],))
            mysql.connection.commit()
            cur.close()

            feedback = 'success'

        else:
            form['email'] = ''
            feedback = 'error'

    return render_template('new_user.html', feedback=feedback, form=form)


@app.route('/profile')
def profile():

    cookie = request.cookies.get('user_data')
    if cookie == None:
        return redirect(url_for('login'))
    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT *
        FROM owner
        WHERE ow_id = %s
            AND ow_status = 'on'
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], ))
    userdata = cur.fetchone()
    cur.close()

    del userdata['ow_password']

    return render_template('/profile.html', user=user, userdata=userdata)


@app.route('/sendpass', methods=['GET', 'POST'])
def sendpass():

    if request.method == 'POST':
        form = dict(request.form)
        sql = '''
            SELECT ow_id, ow_email, ow_name
            FROM owner
            WHERE ow_email = %s
                AND ow_status = 'on'
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], ))
        userdata = cur.fetchone()
        cur.close()

        

        if userdata != None:

            new_password = get_new_password()

            sql = '''
                UPDATE owner
                SET ow_password = SHA1(%s)
                WHERE ow_id = %s
                    AND ow_status = 'on'
            '''
            cur = mysql.connection.cursor()
            cur.execute(sql, (new_password, userdata['ow_id'],))
            mysql.connection.commit()
            cur.close()

            mail_message = f'''
                Olá {userdata['ow_name']}!

                Você pediu uma nova senha de acesso ao "Cadastro de Trecos".

                Use esta senha para fazer login: {new_password}

                Obrigado...
            '''

            resposta = send_email(
                userdata['ow_email'],
                'Cadastro de Itens - nova senha',
                mail_message
            )
            feedback = 'success'
        else:
            feedback = 'error'
            

    return render_template('sendpass.html')


if __name__ == '__main__':
    app.run(debug=True)
