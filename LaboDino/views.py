from .forms import LoginForm, BudgetForm, CampaignForm, SampleForm
from .app import app,db
from .decorators import role_access_rights
from .models import PERSONNEL, CAMPAGNE, ECHANTILLON, ROLE, ECHANTILLON
from flask import render_template,redirect, url_for,request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta

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
        unUser: PERSONNEL = form.authenticate()
        if unUser:
            # Successful login logic here
            login_user(unUser)
            next = form.next.data or url_for("get_campaigns",completed= None)
            return redirect(next)
        else:
            # Failed login logic here
            print("Authentication failed")

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
@role_access_rights(ROLE.direction)
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
        print("Budget Form Data:", date,montant)

    return render_template("budget_page.html", form=form)

@app.route("/campaigns/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def get_campaigns(completed: bool = None):
    """
    Affiche la page de présentation de l"ensembles des campagnes.
    A la route : /campaigns/
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        completed (bool, optional): Filtre les campagnes en fonction de leur statut.
                                     Si True, affiche uniquement les campagnes validées.
                                     Si False, affiche uniquement les campagnes invalides.
                                     Si None, affiche toutes les campagnes.
                                     Par défaut à None.
    
    Returns:
        str: Le rendu du template de la liste des campagnes.

    """

    # getting all campaigns
    if completed is not None:
        data: list[CAMPAGNE] = CAMPAGNE.query.all()
    elif completed:
        data: list[CAMPAGNE] = CAMPAGNE.query.filter_by(valide=True).all()

    else:
        data: list[CAMPAGNE] = CAMPAGNE.query.filter_by(valide=False).all()
    

    # getting the page number from query parameters
    page = request.args.get('page', 1, type=int)
    paginated_data, current_page = _pagination(data, page)

    return render_template("campaign_dashboard.html", campaigns= paginated_data, page= current_page)

@app.route("/campaigns/create/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def create_campaign():
    """
    Affiche le formulaire de création d"une nouvelle campagne et gère la soumission du formulaire.
    A la route : /campaigns/create
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Returns:
        str: Le rendu du template de création de campagne ou une redirection vers la liste des campagnes.
        redirect: Redirige vers la liste des campagnes après la création réussie de la campagne.
    """

    form: CampaignForm = CampaignForm()
    
    if form.validate_on_submit():
        form.create_campaign()
        return redirect(url_for("get_campaigns"))
    
    return render_template("create_campaign.html", form=form)

@app.route("/campaigns/<int:campaign_id>/edit/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def edit_campaign(campaign_id: int):
    """
    Affiche le formulaire d"édition d"une campagne existante et gère la soumission du formulaire.
    A la route : /campaigns/edit/<int:campaign_id> où campaign_id est l'identifiant de la campagne à éditer.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à éditer.
    
    Returns:
        str: Le rendu du template d'édition de campagne ou une redirection vers la liste des campagnes.
    """

    form: CampaignForm = CampaignForm()

    edit_campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()

    if form.validate_on_submit():
    
        form.update(campaign_id= campaign_id)
        print(f"Editing Campaign ID: {campaign_id}")

        return redirect(url_for("get_campaigns"))
    
    # Pre-fill form with existing campaign data only on GET request
    form.plateforme.data = edit_campaign.nom_plateforme
    form.lieu.data = edit_campaign.lieu
    form.startDate.data = edit_campaign.dateDebut
    form.duree.data = edit_campaign.duree
    form.submit.label.text = "Update Campaign"
    
    return render_template("edit_campaign.html", form=form, campaign_id=campaign_id)

@app.route("/campaigns/<int:campaign_id>/delete/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def delete_campaign(campaign_id: int):
    """
    Supprime une campagne existante.
    A la route : /campaigns/delete/<int:campaign_id> où campaign_id est l'identifiant de la campagne à supprimer.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à supprimer.

    Returns:
        redirect: Redirige vers la liste des campagnes après la suppression.
    """

    db.session.delete(CAMPAGNE.query.filter_by(id_campagne=campaign_id).first())
    db.session.commit()
    
    print(f"Deleting Campaign ID: {campaign_id}")
    return redirect(url_for("get_campaigns"))

@app.route("/campaigns/<int:campaign_id>/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def campaign_detail(campaign_id: int):
    """
    Affiche les détails d"une campagne spécifique.
    A la route : /campaigns/<int:campaign_id> ou campaign_id est l'identifiant de la campagne.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à afficher.

    Returns:
        str: Le rendu du template des détails de la campagne.
    """
    campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()

    # Logic to retrieve and display campaign details
    print(f"Campaign ID: {campaign.id_campagne}")
    return render_template("campaign_details.html", campaign=campaign, timedelta=timedelta)

@app.route("/campaigns/<int:campaign_id>/samples/<int:sample_id>")
@login_required
@role_access_rights(ROLE.chercheur)
def sample_detail(sample_id: int, campaign_id: int):
    """
        Affiche les détails d"un échantillon spécifique.

        Args:
            sample_id (int): L'identifiant de l'échantillon à afficher.
        Returns:
            str: Le rendu du template des détails de l'échantillon.
    """

    sample: ECHANTILLON = ECHANTILLON.query.filter_by(id_echantillon=sample_id).first()
    print(f"Sample ID: {sample.id_echantillon}")
    samples : list[ECHANTILLON] = ECHANTILLON.query.all()

    return render_template("sample_details.html", sample=sample, samples=samples)

@app.route("/campaigns/<int:campaign_id>/samples/create/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def create_sample(campaign_id: int):
    """
    Crée un nouvel échantillon.

    Args:
        campaign_id (int): L'identifiant de la campagne à laquelle l'échantillon appartient.

    Returns:
        str: Le rendu du template de création d'échantillon ou une redirection vers la page de détails de la campagne.
        redirect: Redirige vers la page de détails de la campagne après la création réussie de l'échantillon.
    """

    form: SampleForm = SampleForm()
    
    if form.validate_on_submit():
        form.create_sample(campaign_id= campaign_id)
        return redirect(url_for("campaign_detail", campaign_id= campaign_id))
    
    return render_template("create_sample.html", form=form, campaign_id=campaign_id)

@app.route("/campaigns/samples/<int:sample_id>/edit/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def edit_sample(sample_id: int):
    """
    Édite un échantillon existant.

    Args:
        sample_id (int): L'identifiant de l'échantillon à éditer.
    
    Returns:
        str: Le rendu du template d'édition d'échantillon ou une redirection vers la page de détails de l'échantillon.
    """
    form: SampleForm = SampleForm()

    edit_sample: ECHANTILLON = ECHANTILLON.query.filter_by(id_echantillon=sample_id).first()

    if form.validate_on_submit():
    
        form.update(sample_id= sample_id)
        print(f"Editing Sample ID: {sample_id}")

        return redirect(url_for("sample_detail", sample_id= sample_id))
    
    # Pre-fill form with existing campaign data only on GET request
    form.dna_file.data = edit_sample.fichier_sequence_adn
    # TODO: Handle file field pre-filling properly

    form.comment.data = edit_sample.commentaire
    
    if edit_sample.espece:
        form.specie.data = edit_sample.espece

    form.submit.label.text = "Update Sample"
    
    return render_template("edit_sample.html", form=form, sample_id=sample_id)


@app.route("/campaigns/samples/<int:sample_id>/delete/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def delete_sample(sample_id: int):
    """
    Supprime un échantillon existant.
    
    Args:
        sample_id (int): L'identifiant de l'échantillon à supprimer.
    
    Returns:
        redirect: Redirige vers la page de détails de la campagne après la suppression.
    """
    
    sample: ECHANTILLON = ECHANTILLON.query.filter_by(id_echantillon=sample_id).first()
    db.session.delete(sample)
    db.session.commit()
    print(f"Deleting Sample ID: {sample_id}")
    return redirect(url_for("campaign_detail", campaign_id= sample.id_campagne))

def _pagination(data: list, page: int, items_per_page: int = 5) -> tuple[list,int]:
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

    return data[begin:end], page
  