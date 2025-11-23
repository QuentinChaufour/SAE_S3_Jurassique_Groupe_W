
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask ( __name__ )
app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)
# To get one variable, tape app.config['MY_VARIABLE']

# création du lien avec la base de données

# login manager

login_manager = LoginManager(app)
login_manager.login_view = "login"