from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

#set URI for database, enable CSRF for Flask forms
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ToDoList_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #improve db efficiency
app.config['SECRET_KEY'] = 'ThisShouldBeHarderToGuess'

db = SQLAlchemy(app) #instantiate db

#create login manager and set default route
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

