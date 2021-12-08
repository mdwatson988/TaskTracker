from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ToDoList_db.db' #set URI for database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #improve db efficiency
app.config['SECRET_KEY'] = 'ThisShouldBeHarderToGuess' #enable CSRF for Flask forms

db = SQLAlchemy(app) #instantiate db

#create login manager and set default route
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

import models