
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask ( __name__ )
app.config.from_object('config')
db = SQLAlchemy(app)
# To get one variable, tape app.config['MY_VARIABLE']

# création du lien avec la base de données