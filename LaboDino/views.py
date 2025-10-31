from LaboDino.forms import LoginForm
from .app import app
from flask import render_template

@app.route('/')
def home():
    form = LoginForm()
    return render_template('connexion.html', form=form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.authenticate()
        if user:
            # Successful login logic here
            pass
        else:
            # Failed login logic here
            pass
    print("test")
    print(form.id.data)
    print(form.password.data)
    return render_template('connexion.html', form=form)