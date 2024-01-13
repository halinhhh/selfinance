from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1'
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(16), unique=True, nullable=False)
    user_password = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(64), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    account_name = db.Column(db.String(32), nullable=False)
    account_balance = db.Column(db.DECIMAL(10, 0), nullable=False)
    account_type = db.Column(db.Enum('cash', 'savings', 'credit'), nullable=False)
    account_status = db.Column(db.Enum('Active', 'Inactive'), server_default='Active', nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), server_onupdate=db.func.current_timestamp(), nullable=False)

class Transaction(db.Model):
    transactions_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.Enum('Thu', 'Chi', 'Chuyen Khoan'), nullable=False)
    transaction_amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    transaction_description = db.Column(db.Text)

class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    report_type = db.Column(db.Enum('Daily', 'Monthly'), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # For demonstration purposes, check if username is "me" and password is "123456"
        if username == "me" and password == "123456":
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/manage_finance', methods=['GET', 'POST'])
def manage_finance():
    if request.method == 'POST':
        income = float(request.form.get('income', 0))
        interest = float(request.form.get('interest', 0))
        loss = float(request.form.get('loss', 0))
        loaner = float(request.form.get('loaner', 0))

        transaction_date_str = request.form.get('transaction_date')
        if transaction_date_str:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
        else:
            transaction_date = datetime.utcnow()

        net_profit = Decimal(income + interest - loss - loaner)

        account = Account.query.filter_by(user_id=1).first()
        if account:
            # Update account balance
            account.account_balance += net_profit

            # Save data to the database
            transaction = Transaction(
                user_id=1,  
                transaction_type='financial_data',
                transaction_amount=net_profit,
                transaction_date=transaction_date
            )

            db.session.add(transaction)
            db.session.commit()
        else:
            flash('Account not found', 'danger')

    return render_template('manage_finance.html')

@app.route('/manage_account')
def manage_account():
    
    account = Account.query.filter_by(user_id=1).first()
    sample_account = Account(
    user_id=1,
    account_name='Sample Account',
    account_balance=10000,
    account_type='cash',
    account_status='Active'
)


    db.session.add(sample_account)
    db.session.commit()
    
    return render_template('manage_account.html', account=account)

@app.route('/write_report', methods=['GET', 'POST'])
def write_report():
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        report_date_str = request.form.get('report_date')

        if report_date_str:
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
        else:
            report_date = datetime.utcnow()

        flash('Report submitted successfully', 'success')

    return render_template('write_report.html')





if __name__ == '__main__':
    app.run(debug=True)

