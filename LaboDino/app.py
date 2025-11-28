
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask ( __name__ )

app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)
# To get one variable, tape app.config['MY_VARIABLE']

# login manager

login_manager = LoginManager(app)
login_manager.login_view = "login"
