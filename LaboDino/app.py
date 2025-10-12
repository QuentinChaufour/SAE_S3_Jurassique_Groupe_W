
from flask import Flask,render_template

app = Flask ( __name__ )

app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

# création du lien avec la base de données