from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.handlers.sha2_crypt import sha256_crypt




app = Flask(__name__)
app.secret_key = "hasan"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/hasanciftci/Desktop/flask-todo/todo-team.db'
db = SQLAlchemy(app)


################# DB MODELS #################


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120),nullable=False)
    owner_id = db.Column(db.String(120),nullable=False)
    description = db.Column(db.String(120),nullable=False)
    

class Todocuk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.String(120),nullable=False)
    keeper_id = db.Column(db.String(120),nullable=False)
    title = db.Column(db.String(120),nullable=False)
    description = db.Column(db.String(120),nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
 
################# WTFORMS #################

class RegistrationForm(Form):
    username = StringField('Kullanıcı Adı', validators = [validators.DataRequired()])
    email = StringField('E-Posta', validators = [validators.DataRequired()])
    password = PasswordField('Parola', validators = [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Parolalar eşleşmiyor...')])
    confirm = PasswordField('Parola Doğrula', validators = [validators.DataRequired()])


class LoginForm(Form):
    username = StringField('Kullanıcı Adı', validators = [validators.DataRequired()])
    password = PasswordField('Parola', validators = [validators.DataRequired()])


class CreateTodoForm(Form):
    title = StringField('Başlık', validators = [validators.DataRequired(), validators.Length(min = 3, max = 30)])
    description = StringField('Açıklama', validators = [validators.DataRequired(),validators.Length(min = 3, max = 120)])



################# ROUTES #################

@app.route('/', methods = ["GET","POST"])
def index():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        password = sha256_crypt.encrypt(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            flash("Kaydolmayı başardın, tebrikler!","success")
        except:
            flash("Başaramadın, girdiğin bilgiler ile kayıtlı bir kullanıcı var!","info")
            
        
        return render_template('index.html',form = form)
    else:
        return render_template('index.html',form = form)

@app.route('/login', methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        entered_username = form.username.data
        entered_password = form.password.data
        query = User.query.filter_by(username=entered_username)
        try:
            user = query.one()
        except:
            flash("Böyle biri yok, ne yapmaya çalışıyorsun?","warning")
            return redirect(url_for("login"))

        if sha256_crypt.verify(entered_password,user.password):
            flash("Giriş yapmayı başardın, tebrikler!","success")
            session["logged_in"] = True
            session["logged_user"] = user.username
            return redirect(url_for("index"))
        else:
            flash("Giriş yapmayı başarmadın...","danger")
            return redirect(url_for("index"))

    else:
        return render_template('login.html',form = form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/createtodo', methods = ["POST", "GET"])
def createtodo():
    form = CreateTodoForm(request.form)
    if request.method == "POST" and form.validate():
        todo = Todo(title=form.title.data,owner_id=session["logged_user"],description=form.description.data)
        db.session.add(todo)
        db.session.commit()
        flash("Sana iş çıktı! ToDo başarıyla oluşturuldu!","info")
        return redirect(url_for("listtodo"))
    else:
        return render_template("createtodo.html",form=form)

@app.route('/listtodo')
def listtodo():
    query = Todo.query.filter_by(owner_id = session["logged_user"])
    try:
        todos = query.all()
    except:
        flash("Buralar eskiden hep dutluktu... Hala da öyle...","warning")
        return redirect(url_for("createtodo"))
    return render_template("listtodo.html",todos = todos)


if __name__ == "__main__":  
    db.create_all()
    app.run(debug = True)
