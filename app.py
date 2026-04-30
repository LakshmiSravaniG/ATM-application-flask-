from flask import Flask, request, redirect, url_for, render_template, make_response, jsonify
from datetime import datetime
app = Flask(__name__)
users = {}  # to store user data
statements = {}  # to store statements of users


@app.route('/')
def home():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
        username = request.form['username']
        userpassword = request.form['password']
        user_pinno = request.form['userpinno']
        if username not in users:
            users[username] = {'user_password': userpassword,
                               'user_pinno': user_pinno, 'Amount': 0}
            print(users)
            if username not in statements:
                statements[username] = {
                    'Deposit_statements': [], 'Withdraw_statements': []}

            return redirect(url_for('login'))
        else:
            return 'user already existed'

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_username = request.form['username']
        login_password = request.form['password']

        if login_username in users:
            if users[login_username]['user_password'] == login_password:
                resp = make_response(redirect(url_for('dashboard')))
                resp.set_cookie('user', login_username)
                return resp
            else:
                return 'password wrong'
        else:
            return 'Username was wrong'
    return render_template('login.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if request.cookies.get('user'):
        return render_template('dashboard.html')
    else:
        return 'pls login view dashboard'


@app.route('/deposit', methods=['GET', 'PUT'])
def deposit():
    if request.cookies.get('user'):
        if request.method == 'PUT':
            username = request.cookies.get('user')
            print(request.get_json())
            deposit_amount = int(request.get_json()['amount'])  # 500
            if deposit_amount > 0:
                if deposit_amount % 100 == 0:
                    if deposit_amount <= 50000:
                        users[username]['Amount'] = users[username]['Amount'] + \
                            deposit_amount
                        deposit_time = datetime.now()
                        deposit_data = (deposit_amount, deposit_time)
                        statements[username]['Deposit_statements'].append(
                            deposit_data)
                        return f'{deposit_amount}'
                    else:
                        return jsonify({'message': 'Amount should be <= 50000'})
                else:
                    return jsonify({'message': 'Amount should be multiples of 100'})
            else:
                return jsonify({'message': 'Amount should be > 0'})
        return render_template('deposit.html')
    else:
        return 'pls login view deposit'


@app.route('/withdraw', methods=['GET', 'PUT'])
def withdraw():
    if request.cookies.get('user'):
        if request.method == 'PUT':
            username = request.cookies.get('user')
            print(request.get_json())

            withdraw_amount = int(request.get_json()['amount'])
            balance_amount = users[username]['Amount']

            if withdraw_amount > 0:
                if withdraw_amount % 100 == 0:
                    if withdraw_amount <= balance_amount:
                        users[username]['Amount'] = balance_amount - \
                            withdraw_amount
                        withdraw_time = datetime.now()
                        withdraw_data = (withdraw_amount, withdraw_time)
                        statements[username]['Withdraw_statements'].append(
                            withdraw_data)
                        return jsonify({'message': f'{users[username]['Amount']} after withdraw'})
                    else:
                        return jsonify({'message': 'Insufficient balance'})
                else:
                    return jsonify({'message': 'Amount should be multiples of 100'})
            else:
                return jsonify({'message': 'Amount should be > 0'})

        return render_template('withdraw.html')

    else:
        return 'pls login view withdraw'


@app.route('/balance', methods=['GET'])
def balance():
    if request.cookies.get('user'):
        username = request.cookies.get('user')
        balance_amount = users[username]['Amount']
        return render_template('balance.html', balance_amount=balance_amount, users=users)
    else:
        return redirect(url_for('login'))


@app.route('/userstatements', methods=['GET'])
def userstatements():
    if request.cookies.get('user'):
        username = request.cookies.get('user')
        deposit_userstatements = statements[username]['Deposit_statements']
        withdraw_userstatements = statements[username]['Withdraw_statements']
        return render_template('statements.html', deposit_userstatements=deposit_userstatements, withdraw_userstatements=withdraw_userstatements)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if request.cookies.get('user'):
        resp = redirect(url_for('home'))
        resp.delete_cookie('user')   # cleaner way to remove cookie
        return resp
    else:
        return 'user not found'


app.run(use_reloader=True, debug=True)
