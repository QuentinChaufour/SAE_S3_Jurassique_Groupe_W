from .forms import LoginForm, BudgetForm
from .app import app, users_storage
from .decorators import role_access_rights
from .enums import UserRole
from flask import render_template,redirect, url_for,request
from flask_login import login_user, logout_user, login_required

@app.route("/")
def home():

    return redirect(url_for("login"))
    #return render_template("campaign_details.html",campaign_id= 2 ,participants= {1:["a","b","c"],2:["d","e"]})

@app.route("/login/", methods=["GET", "POST"])
def login():
    """Affiche le formulaire de connexion et gère la soumission du formulaire."""
    form = LoginForm()

    if not form.is_submitted():
        form.next.data = request.args.get("next")

    elif form.validate_on_submit():
        unUser = form.authenticate()
        if unUser:
            # Successful login logic here
            users_storage[unUser.id] = unUser
            login_user(unUser)
            next = form.next.data or url_for("campaign_detail", campaign_id=2)
            return redirect(next)
        else:
            # Failed login logic here
            print("Authentication failed")

    print(form.id.data)
    print(form.password.data)
    return render_template("login.html", form=form)

@app.route("/logout/")
def logout():
    """Déconnecte l'utilisateur actuel."""
    logout_user()
    return redirect(url_for("login"))

@login_required
@app.route("/budget/", methods=["GET", "POST"])
def set_budget():
    """Affiche le formulaire de définition du budget et gère la soumission du formulaire."""

    form = BudgetForm()

    if form.validate_on_submit():
        date, montant = form.add_budget()
        # Logic to handle the budget submission
        pass
    print("Budget Form Data:", form.date.data, form.montant.data)
    

    return render_template("budget_page.html", form=form)

@login_required
@app.route("/campaigns/", methods=["GET", "POST"])
def get_campaigns():
    """Affiche la page de présentation de l"ensembles des campagnes."""

    # Logic to retrieve and display campaigns

    return render_template("campaign_dashboard.html", campaigns= [2,46,67])

@app.route("/campaigns/<int:campaign_id>")
@login_required
@role_access_rights(UserRole.TECHNICIAN,UserRole.ADMIN)
def campaign_detail(campaign_id):
    """Affiche les détails d"une campagne spécifique."""
    # Logic to retrieve and display campaign details
    print(f"Campaign ID: {campaign_id}")
    return render_template("campaign_details.html", campaign_id=campaign_id, participants= {1:["a","b","c"],2:["d","e"]})

       