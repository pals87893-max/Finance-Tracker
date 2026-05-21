from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from sqlalchemy import func,exists
import calendar
load_dotenv()
app=Flask(__name__)
app.secret_key = "39f44bddb56576c4a39a7106c7a682b3e63c03a833765ed69900f73d6e16ec64"
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///Expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db=SQLAlchemy(app)
CATEGORIES = ['Food', 'House expences', 'Entertainment','Work Expences']
now =datetime.now()
def get_user_expense_model(username):
    class Expense(db.Model):
            __tablename__ = f'expence_{username}'
            __table_args__ = {'extend_existing': True}
            sl_no=db.Column(db.Integer,primary_key=True)
            ammount=db.Column(db.Float)
            catagory = db.Column(db.String(200), nullable=False)
            date=db.Column(db.String, nullable=False)
            name=db.Column(db.String(200), nullable=False)

            def __repr__(self)-> str:
                return f"{self.name} - {self.ammount}"
    return Expense
def get_user_budget_model(username):
    class Budget(db.Model):
            __tablename__ = f'budget_{username}'
            __table_args__ = {'extend_existing': True}
            # __tablename__ = f'todo_{username}'
            # __table_args__ = {'extend_existing': True}
            sl_no=db.Column(db.Integer,primary_key=True)
            budget=db.Column(db.Float)
            month=db.Column(db.String, nullable=False)
    return Budget

class Login(db.Model):
        sl_no=db.Column(db.Integer,primary_key=True)
        user_email=db.Column(db.String, nullable=False)
        password=db.Column(db.String(20), nullable=False)
        Username=db.Column(db.String(200),nullable=False)


@app.route('/sign in',methods=['GET','POST'])
def Sign_in():
    error=None
    if request.method=='POST':
        user_email=request.form.get('user_email')      
        password=request.form.get('Password')
        username=request.form.get('username')
        sign_in=Login(user_email=user_email, password=password, Username=username)
        user = Login.query.filter_by(user_email=user_email).first()
        if user and user.user_email == user_email:
            error="Email already exist select a diferent one or log in"
        else:
            db.session.add(sign_in)
            db.session.commit()
            Username=Login.query.filter_by(Username=username).first()
            return redirect(url_for('home',username=Username))
    sign_details=Login.query.all()
    return render_template("sign_in.html",sign_details=sign_details,error=error)
@app.route('/', methods=['GET','POST'])
def login():
    error=None
    if request.method=='POST':
        user_email=request.form.get('user_email')
        password=request.form.get('Password')
        user = Login.query.filter_by(user_email=user_email).first()
        
        if user and user.password == password:
            session['username']= user.Username
            return redirect(url_for('home'))
        else:
            error="Couldn't found the email plaease Sign In first"

    return render_template('login.html',error=error)


@app.route('/home',methods=['GET','POST'])
def home():
    username=session.get('username')
    Budget = get_user_budget_model(username)
    Expense= get_user_expense_model(username)
    db.create_all()
    error=None
    if request.method=='POST':
        Budget.query.delete()
        Expense.query.delete()
        db.session.commit()
        budget=float(request.form.get('budget'))
        date=request.form.get('Month')
        Budget.query.filter_by(month=date).delete()
        if budget<0:
            error='Set a positive number'
        else:
            db.session.add(Budget(month=date,budget=budget))
            db.session.commit()
    allBudget=Budget.query.all()
    return render_template('index.html',allBudget=allBudget,error=error)

@app.route('/add_Expense',methods=['GET','POST'])
def expenses():
    username=session.get('username')
    Budget=get_user_budget_model(username)
    Expense= get_user_expense_model(username)
    db.create_all()
    if request.method=='POST':
        name=request.form.get('name')
        amount=request.form.get('amount')
        category=request.form.get('category')
        date=calendar.month_name[int(now.strftime("%m"))]
        expense=Expense(name=name,ammount=amount,catagory=category,date=date)
        db.session.add(expense)
        db.session.commit()
    allExpence=Expense.query.all()
    allBudget=Budget.query.all()
    return render_template("enrty.html",allExpence=allExpence,allBudget=allBudget)

@app.route('/finance',methods=["GET",'POST'])
def finance():
    username=session.get('username')
    Budget = get_user_budget_model(username)
    Expense= get_user_expense_model(username)
    db.create_all()
    if request.method=='POST':
        name=request.form.get('name')
        amount=request.form.get('amount')
        category=request.form.get('category')
        date=calendar.month_name[int(now.strftime("%m"))]
        expense=Expense(name=name,ammount=amount,catagory=category,date=date)
        budget=float(request.form.get('budget'))
        date=request.form.get('Month')
        db.session.add(Budget(month=date,budget=budget))
        db.session.add(expense)
        db.session.commit()
    allExpence=Expense.query.all()
    allBudget=Budget.query.all()
    category_totals=db.session.query(Expense.catagory, func.sum(Expense.ammount).label('total')).group_by(Expense.catagory).all()
    total_amount={cat: total for cat,total in category_totals}
    return render_template('read.html',allExpence=allExpence,allBudget=allBudget, category=CATEGORIES,total_amount=total_amount)


@app.route('/update/<int:sl_no>', methods=['GET','POST'])
def update(sl_no):
    username=session.get('username')
    Expense= get_user_expense_model(username)
    db.create_all()
    mistake= Expense.query.filter_by(sl_no=sl_no).first()
    if request.method=='POST':
        mistake.name=request.form.get('name')
        mistake.ammount=request.form.get('amount')
        mistake.catagory=request.form.get('category')
        db.session.commit()
        return redirect(url_for('finance'))
    return render_template("update.html",mistake=mistake)
     
@app.route('/delete/<int:sl_no>')
def delete(sl_no):
    username=session.get('username')
    Expense= get_user_expense_model(username)
    db.create_all()
    wrong=Expense.query.filter_by(sl_no=sl_no).first()
    db.session.delete(wrong)
    db.session.commit()
    return redirect(url_for('finance'))
if __name__ == '__main__':
    app.run(debug=True)
