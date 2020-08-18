from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/hasanciftci/Desktop/flask-todo/todo-team.db'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)


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
 


if __name__ == "__main__":  
    db.create_all()
    app.run(debug = True)
