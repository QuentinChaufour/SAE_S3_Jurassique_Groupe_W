from LaboDino.forms import LoginForm, BudgetForm
from .app import app
from flask import render_template

@app.route('/')
def home():
    return render_template('show_campaigns.html', campaigns= [2,46,67])

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """Affiche le formulaire de connexion et gère la soumission du formulaire."""

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

@app.route('/budget/', methods=['GET', 'POST'])
def set_budget():
    """Affiche le formulaire de définition du budget et gère la soumission du formulaire."""

    form = BudgetForm()

    if form.validate_on_submit():
        date, montant = form.add_budget()
        # Logic to handle the budget submission
        pass
    print("Budget Form Data:", form.date.data, form.montant.data)
    

    return render_template('budget_page.html', form=form)

@app.route('/campaigns/', methods=['GET', 'POST'])
def get_campaigns():
    """Affiche la page de présentation de l'ensembles des campagnes."""

    return render_template('show_campaigns.html', campaigns= [2,46,67])

@app.route('/campaigns/<int:campaign_id>')
def campaign_detail(campaign_id):
    """Affiche les détails d'une campagne spécifique."""
    print(f"Campaign ID: {campaign_id}")