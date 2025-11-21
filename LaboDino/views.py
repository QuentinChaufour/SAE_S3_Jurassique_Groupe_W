from .forms import LoginForm, BudgetForm
from .app import app, users_storage
from .decorators import role_access_rights
from .enums import UserRole
from flask import render_template,redirect, url_for,request
from flask_login import login_user, logout_user, login_required

@app.route("/")
def home():

    return redirect(url_for("get_campaigns"))
    #return render_template("campaign_details.html",campaign_id= 2 ,participants= {1:["a","b","c"],2:["d","e"]})

@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Affiche le formulaire de connexion et gère la soumission du formulaire.
    A la route : /login/
    En cas de succès, redirige vers le menu selon le role de l'utilisateur.
    """
    
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
    """
    Déconnecte l'utilisateur actuel.
    A la route : /logout/
    Et le redirige vers la page de connexion.
    """

    logout_user()
    return redirect(url_for("login"))

@app.route("/budget/", methods=["GET", "POST"])
@login_required
@role_access_rights(UserRole.DIRECTION)
def set_budget():
    """
    Affiche le formulaire de définition du budget et gère la soumission du formulaire.
    A la route : /budget/
    N'est accessible qu'aux utilisateurs avec les rôles DIRECTION.
    """

    form = BudgetForm()

    if form.validate_on_submit():
        date, montant = form.add_budget()
        # Logic to handle the budget submission
        pass
    print("Budget Form Data:", form.date.data, form.montant.data)
    

    return render_template("budget_page.html", form=form)

@login_required
@app.route("/campaigns/", methods=["GET", "POST"])
@role_access_rights(UserRole.RESEARCHER)
def get_campaigns():
    """
    Affiche la page de présentation de l"ensembles des campagnes.
    A la route : /campaigns/
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.
    """

    # getting all campaigns
    data = [2,46,67,89,23,12,45,78,90,11,34,56]  # Example data

    # getting the page number from query parameters
    page = request.args.get('page', 1, type=int)

    return render_template("campaign_dashboard.html", campaigns= _pagination(data, page), page= page)

@app.route("/campaigns/create/", methods=["GET", "POST"])
@login_required
@role_access_rights(UserRole.RESEARCHER)
def create_campaign():
    """
    Affiche le formulaire de création d"une nouvelle campagne et gère la soumission du formulaire.
    A la route : /campaigns/create
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.
    """

    # TODO
    pass

@app.route("/campaigns/<int:campaign_id>/", methods=["GET", "POST"])
@login_required
@role_access_rights(UserRole.RESEARCHER)
def campaign_detail(campaign_id):
    """
    Affiche les détails d"une campagne spécifique.
    A la route : /campaigns/<int:campaign_id> ou campaign_id est l'identifiant de la campagne.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à afficher.
    """

    # Logic to retrieve and display campaign details
    print(f"Campaign ID: {campaign_id}")

    return render_template("campaign_details.html", campaign_id=campaign_id, participants= {1:["a","b","c"],2:["d","e"]})

def _pagination(data: list, page: int, items_per_page: int = 5) -> list:
    """Pagine les données en fonction de la page et du nombre d"éléments par page.
    
    Args:
        data (list): La liste des données à paginer.
        page (int): Le numéro de la page actuelle (1-indexed).
        items_per_page (int, optional): Le nombre d"éléments par page. Par défaut à 5.
    
    Returns:
        list: La sous-liste des données correspondant à la page demandée.
    """

    # checking bounds for pagination
    if page < 1:
        page = 1
    elif page > (len(data) - 1) // items_per_page + 1:
        page = (len(data) - 1) // items_per_page + 1

    begin: int = (page - 1) * items_per_page
    end: int = begin + items_per_page

    return data[begin:end]