from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.handlers.sha2_crypt import sha256_crypt
from functools import wraps


app = Flask(__name__)
app.secret_key = "hasan"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/hasanciftci/Desktop/flask-todo/todo-team.db'
db = SQLAlchemy(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu alanı görüntülemek için kullanıcı girişi yapmalısınız.","danger")
            return redirect(url_for("login"))
    return decorated_function

# Log out required
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            flash("Zaten giriş yaptın!","info")
            return redirect(url_for("mine"))
        else:
            return f(*args, **kwargs)
    return decorated_function


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
    complete = db.Column(db.Boolean)
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


class CreateTodocukForm(Form):
    title = StringField('Başlık', validators = [validators.DataRequired()])
    description = StringField('Açıklama', validators = [validators.DataRequired()])
    keeper_id = StringField('Katılımcılar', validators = [validators.DataRequired()])


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

@app.route('/login', methods = ["GET", "POST"])
@logout_required
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
            return redirect(url_for("mine"))
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
@login_required
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
@login_required
def listtodo():
    query = Todo.query.filter_by(owner_id = session["logged_user"])
    todos = query.all()
    if bool(todos):
        return render_template("listtodo.html",todos = todos)
    else:
        flash("Buralar eskiden hep dutluktu... Hala da öyle...","warning")
        return redirect(url_for("createtodo"))
    

#login decorator needed
@app.route('/todo/<string:id>',methods = ["POST","GET"])
@login_required
def showtodo(id):
    todocuklar = Todocuk.query.filter_by(todo_id = id).all()
    form = CreateTodocukForm(request.form)
    isAdmin = False
    isKeeper = False
    #toggle show adding todocuk panel
    if bool(Todo.query.filter_by(id = id, owner_id = session["logged_user"]).first()):
        isAdmin = True
    #toggle show todocuks 
    if bool(Todocuk.query.filter_by(todo_id = id, keeper_id = session["logged_user"]).first()):
        isKeeper = True
    if request.method == "POST" and form.validate():
        title = form.title.data
        description = form.description.data
        keeper = form.keeper_id.data
        keepers = keeper.split(',')
        for keeper in keepers:
            #filter not existed user relation with todocuk
            if not bool(User.query.filter_by(username=keeper).first()):
                continue
            todocuk = Todocuk(todo_id = id, keeper_id = keeper, title = title, description = description, complete=False)
            db.session.add(todocuk)
            db.session.commit()
        flash("ToDocuk, ToDo'ya eklendi, kolay gelsin!","info")
        return redirect(url_for('listtodo'))
    else:
        #GET Request
        return render_template('todo.html',form = form, todocuklar=todocuklar, isAdmin=isAdmin, isKeeper=isKeeper)
      
@app.route('/mine')
@login_required
def mine():
   #kendisine ait todocukların idlerini bul 
    #bu todocukları içeren todoları listele
    todo_involved_me = Todocuk.query.with_entities(Todocuk.todo_id).filter_by(keeper_id = session["logged_user"]).all()
    result = [r for r, in todo_involved_me]
    query = Todo.query.filter(Todo.id.in_(result))
    minetodos = query.all()

    if bool(minetodos):
        return render_template("minetodo.html",minetodos = minetodos)
    else:
        flash("Buralar eskiden hep dutluktu... Hala da öyle...","warning")
        return redirect(url_for("createtodo"))
    

@app.route('/complete/<string:id>')
@login_required
def completetodocuk(id):
    try:
        todocuk = Todocuk.query.filter_by(keeper_id = session["logged_user"], id=id).one()
        todocuk.complete = 1
        db.session.commit()
        flash("Bir görevi tamamladın, bravo!","success")
        return redirect(url_for("mine"))
        
    except:
        flash("Bu işlem için yetkiniz yok!","danger")
        return redirect(url_for("mine"))

    return render_template("completetodocuk.html")

if __name__ == "__main__":  
    db.create_all()
    app.run(debug = True)
