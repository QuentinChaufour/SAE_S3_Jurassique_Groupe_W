from LaboDino.forms import LoginForm, PlatformCreationForm      
from .app import app, db
from flask import redirect, render_template, request, url_for
from LaboDino.models import Personnel, Plateforme

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

@app.route('/choice_action_tech/')
def tech_choice_action():
    return render_template('technical_choice.html')

@app.route('/choice_action_tech/platform_management/', methods=['GET', 'POST'])
def platform_management():
    form = PlatformCreationForm()

    if form.validate_on_submit():
        platform = Plateforme(
            nom_plateforme=form.nom_plateforme.data,
            nb_personnes_requises=form.nb_personnes_requises.data,
            cout_journalier=form.cout_journalier.data,
            intervalle_maintenance=form.intervalle_maintenance.data
        )
        db.session.add(platform)
        print(platform)
        db.session.commit()
        return redirect(url_for('platform_management'))
    platforms = Plateforme.query.all()

    return render_template('platform_management.html', form=form, platforms=platforms)