from .forms import LoginForm, BudgetForm, CampaignForm, SampleForm, EquipmentForm, PlatformForm, MaintenanceForm
from .app import app,db
from .decorators import role_access_rights
from .models import PERSONNEL, CAMPAGNE, ECHANTILLON, ROLE, ECHANTILLON,PARTICIPER_CAMPAGNE, BUDGET, EQUIPEMENT, ESPECE, PLATEFORME, MAINTENANCE
from flask import render_template,redirect, url_for,request,jsonify,flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, date
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import extract,func
import json
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
from matplotlib import pyplot as plt


@app.route("/")
def home():

    return redirect(url_for("login"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Affiche le formulaire de connexion et gère la soumission du formulaire.
    En cas de succès, redirige vers le menu selon le role de l'utilisateur.
    """
    
    form = LoginForm()

    form.next.data = request.args.get("next")


    if form.validate_on_submit():
        un_user: PERSONNEL = form.authenticate()
        if un_user:
            login_user(un_user)

            next: str = form.next.data

            if next is None or next == "":
            
                match(un_user.role):
                    case ROLE.direction:
                        next = url_for("set_budget")
                    case ROLE.chercheur:
                        next = url_for("menu_researcher", completed=None)
                    case ROLE.technicien:
                        next = url_for("menu_technician")
                        #next = url_for("get_equipments")
                    case ROLE.direction:
                        next = url_for("set_budget")
                    case ROLE.administratif:
                        next = url_for("gestion_personnel")
                    case default:
                        next = url_for("login")

            print(f"Redirecting to: {next}")
            return redirect(next)
        else:
            # Failed login logic here
            print("Authentication failed")

    return render_template("login.html", form=form)


@app.route('/menu_technician/')
@login_required
@role_access_rights(ROLE.technicien)
def menu_technician():
    return render_template('technical_choice.html')


@app.route('/menu_technician/platform_management/', methods=['GET', 'POST'])
@login_required
@role_access_rights(ROLE.technicien)
def platform_management():

    if request.method == 'POST':
        filtre = request.form.get('filtre')
    else:
        filtre = request.args.get('filtre')
    
    query = PLATEFORME.query

    print("FILTRE", filtre)
    match filtre:
        case 'nom':
            query = query.order_by(PLATEFORME.nom_plateforme)
        case 'nb_personnes_requises':
            query = query.order_by(PLATEFORME.nb_personnes_requises)
        case 'cout_journalier':
            query = query.order_by(PLATEFORME.cout_journalier)
        case default:
            query = query.order_by(PLATEFORME.nom_plateforme)
    
    form = PlatformForm()
    if form.validate_on_submit():
        form.create_platform(filtre)
    
    data = query.all()  

    page = request.args.get('page', 1, type=int)

    plateforms, page = _pagination(data, page)

    return render_template('platform_management.html', form=form, platforms= plateforms, page= page, filtre_actif=filtre)

@app.route("/menu_technician/platform_management/<string:platform_name>/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.technicien)
def platform_detail(platform_name):

    form = PlatformForm()
    if form.validate_on_submit():
        form.modify_platform()

    platform = PLATEFORME.query.filter_by(nom_plateforme=platform_name).first()

    print(f"Campaign ID: {platform_name}")
    return render_template("platform_details.html", platform=platform, form=form)

@app.route('/menu_technician/platform_management/delete/', methods=['POST'])
def delete_plateforme():

    nom_plateform = request.form.get("nom_plateforme")
    platform = PLATEFORME.query.get(nom_plateform)
    if platform:
        db.session.delete(platform)
        db.session.commit()

    filtre = request.values.get('filtre')
    return redirect(url_for('platform_management', filtre=filtre))

@app.route('/menu_technician/maintenance_management/', methods=['GET', 'POST'])
@login_required
@role_access_rights(ROLE.technicien)
def maintenance_management():
    """
    Permet de visualiser l'ensemble des maintenances, de filtrer la vue selon
    certains paramètres, de supprimer des maintenances 
    et de créer une maintenance pour une plateforme qui existe et pour une date dans le futur.
    A la route : /menu_technician/maintenance_management/
    """
    if request.method == 'POST':
        filtre = request.form.get('filtre')
    else:
        filtre = request.args.get('filtre')
    
    query = MAINTENANCE.query

    print("FILTRE", filtre)
    match filtre:
        case 'date':
            query = query.order_by(MAINTENANCE.date_maintenance)
        case 'duree':
            query = query.order_by(MAINTENANCE.duree_maintenance)
        case 'plateforme':
            query = query.order_by(MAINTENANCE.nom_plateforme)
        case default:
            query = query.order_by(MAINTENANCE.date_maintenance)
    
    form = MaintenanceForm()
    if form.validate_on_submit():
        form.create_maintenance(filtre)
    
    data = query.all()  
    page = request.args.get('page', 1, type=int)

    maintenances, page = _pagination(data, page)

    return render_template('maintenance_management.html', form=form, maintenances=maintenances, page= page, filtre_actif=filtre)

@app.route("/menu_technician/maintenance_management/<string:platform_name>/<string:date_maintenance>", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.technicien)
def maintenance_detail(platform_name, date_maintenance):
    """
    Affiche les détails d'une maintenance sélectionnée
    avec la possibilité de la modifier.
    A la route : /menu_technician/maintenance_management/<string:platform_name>/<string:date_maintenance>
    où "platform_name" est le nom de la plateforme de la maintenance et "date_maintenance" la date de début de la maintenance
    """
    date = datetime.strptime(date_maintenance, '%Y-%m-%d').date()
    form = MaintenanceForm()
    if form.validate_on_submit():
        form.modify_maintenance(platform_name, date_maintenance)

    maintenance = MAINTENANCE.query.filter_by(nom_plateforme=platform_name, date_maintenance=date).first()
    if not maintenance:
        return redirect(url_for('maintenance_management'))
    
    print(f"MAINTENANCE Plateforme: {platform_name}, Date: {date_maintenance}")
     
    return render_template("maintenance_details.html", maintenance=maintenance, form=form)

@app.route('/menu_technician/maintenance_management/delete/', methods=['POST'])
def delete_maintenance():
    """
    Supprime la maintenance sélectionnée
    """

    nom_plateforme = request.form.get("nom_plateforme")
    date_maintenance = request.form.get("date_maintenance")
    maintenance = MAINTENANCE.query.filter_by(nom_plateforme=nom_plateforme, date_maintenance=date_maintenance).first()
    
    if maintenance:
        db.session.delete(maintenance)
        db.session.commit()

    filtre = request.values.get('filtre')
    return redirect(url_for('maintenance_management', filtre=filtre))

@app.route("/logout/")
def logout():
    """
    Déconnecte l'utilisateur actuel.
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
    N'est accessible qu'aux utilisateurs avec les rôles DIRECTION.
    """

    # Créer le graph
    _budget_graph()

    form = BudgetForm()

    # current budget if exists
    curr_date: datetime.date = datetime.now()
    current_budget: BUDGET = BUDGET.query.filter(
            extract('year', BUDGET.date_mois_annee) == curr_date.year,
            extract('month', BUDGET.date_mois_annee) == curr_date.month
        ).first()

    remaining_budget: float = None
    curr_budget_value: float = None

    if current_budget is not None:
        remaining_budget = db.session.query(func.remainingBudget(curr_date)).scalar()
        curr_budget_value = current_budget.budget_total

    if form.validate_on_submit():
        date, montant = form.add_budget()
        
        budget: BUDGET = BUDGET.query.filter(
            extract('year', BUDGET.date_mois_annee) == date.year,
            extract('month', BUDGET.date_mois_annee) == date.month
        ).first()

        try:
            if budget is not None:
                budget.budget_total = montant
                db.session.commit()

            else:
                new_budget = BUDGET(date_mois_annee= date, budget_total= montant)
                db.session.add(new_budget)
                db.session.commit()
        
        except OperationalError as e:
            print(e)
            # TODO

        print("Budget Form Data:", date,montant)
        # Production du graphe
        # possibilité d'ajouter des filtres/paramètres

    return render_template("budget_page.html", form=form, remaining_budget= remaining_budget, total_budget= curr_budget_value)



@app.route("/budget/get_budget/", methods=["GET"])
@login_required
@role_access_rights(ROLE.direction)
def get_budget():
    """
    Récupère le montant du budget pour un mois et une année donnés.
    Pour mettre a jour dynamiquement le formulaire de budget.
    """
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"montant": None})

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"montant": None})

    budget = BUDGET.query.filter(
        extract('year', BUDGET.date_mois_annee) == date.year,
        extract('month', BUDGET.date_mois_annee) == date.month
    ).first()

    if budget:
        return jsonify({"montant": budget.budget_total})
    else:
        return jsonify({"montant": None})


@app.route("/researcher/",methods=["GET"])
def menu_researcher():
    return render_template("menu_chercheur.html")



@app.route("/campaigns/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def get_campaigns(completed: bool = None):
    """
    Affiche la page de présentation de l"ensembles des campagnes.
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
    completed = request.args.get("completed", default= completed, type= str)
    print(f"Completed filter value: {completed}")

    # getting all campaigns
    if completed is None:
        data: list[CAMPAGNE] = CAMPAGNE.query.order_by(CAMPAGNE.dateDebut.desc()).all()
        print(f"Fetching all campaigns without filtering. Total campaigns fetched: {len(data)}")
    elif completed == "True":
        data: list[CAMPAGNE] = CAMPAGNE.query.filter_by(valide=True).all()
        print(f"Filtering for completed campaigns. Total campaigns fetched: {len(data)}")
    else:
        data: list[CAMPAGNE] = CAMPAGNE.query.filter_by(valide=False).all()
        print(f"Filtering for incomplete campaigns. Total campaigns fetched: {len(data)}")

    # getting the page number from query parameters
    page = request.args.get('page', 1, type=int)
    paginated_data, current_page = _pagination(data, page)
    print(paginated_data)

    return render_template("campaign_dashboard.html", campaigns= paginated_data, page= current_page)



@app.route("/campaigns/create/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def create_campaign():
    """
    Affiche le formulaire de création d"une nouvelle campagne et gère la soumission du formulaire.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Returns:
        str: Le rendu du template de création de campagne ou une redirection vers la liste des campagnes.
        redirect: Redirige vers la liste des campagnes après la création réussie de la campagne.
    """

    form: CampaignForm = CampaignForm()

    if form.validate_on_submit():
        try:
            form.create_campaign()
            flash("Campaign created successfully.")
            return redirect(url_for("get_campaigns"))
        except OperationalError as e:
            flash(f"Database error occurred while creating campaign: {e}", category="error")
    
    return render_template("create_campaign.html", form=form)



@app.route("/campaigns/<int:campaign_id>/edit/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def edit_campaign(campaign_id: int):
    """
    Affiche le formulaire d"édition d"une campagne existante et gère la soumission du formulaire.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à éditer.
    
    Returns:
        str: Le rendu du template d'édition de campagne ou une redirection vers la liste des campagnes.
    """

    form: CampaignForm = CampaignForm()

    update_campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()

    if form.validate_on_submit():
        try:
            form.update(campaign_id= campaign_id)
            print(f"Editing Campaign ID: {campaign_id}")
            flash("Campaign updated successfully.")

            return redirect(url_for("campaign_detail", campaign_id= campaign_id))
        except OperationalError as e:
            flash(f"Database error occurred while updating campaign: {e}", category="error")
    
    # Pre-fill form with existing campaign data only on GET request
    form.plateforme.data = update_campaign.nom_plateforme
    form.lieu.data = update_campaign.lieu
    form.startDate.data = update_campaign.dateDebut
    form.duree.data = update_campaign.duree
    form.submit.label.text = "Update Campaign"
    
    return render_template("edit_campaign.html", form=form, campaign_id=campaign_id)



@app.route("/campaigns/<int:campaign_id>/delete/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def delete_campaign(campaign_id: int):
    """
    Supprime une campagne existante.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à supprimer.

    Returns:
        redirect: Redirige vers la liste des campagnes après la suppression.
    """

    campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()
    if campaign is None:
        flash("Campaign not found.", category="error")
        return redirect(url_for("get_campaigns"))
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted successfully.", category="error")
    
    return redirect(url_for("get_campaigns"))



@app.route("/campaigns/<int:campaign_id>/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def campaign_detail(campaign_id: int):
    """
    Affiche les détails d"une campagne spécifique.
    N'est accessible qu'aux utilisateurs avec les rôles RESEARCHER.

    Args:
        campaign_id (int): L"identifiant de la campagne à afficher.

    Returns:
        str: Le rendu du template des détails de la campagne.
    """
    campaign: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()

    is_participating: bool = current_user.id_personnel in [personnel.id_personnel for personnel in campaign.participerCampagne]

    print(f"Campaign ID: {campaign.id_campagne}")
    return render_template("campaign_details.html", campaign=campaign, timedelta=timedelta, is_participating=is_participating)



@app.route("/campaigns/<int:campaign_id>/enroll/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def enroll_campaign(campaign_id: int):
    """
    Inscrit l'utilisateur actuel à une campagne spécifique.

    Args:
        campaign_id (int): L'identifiant de la campagne à laquelle s'inscrire.

    Returns:
        redirect: Redirige vers la page de détails de la campagne après l'inscription.
    """
    participation: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE.query.filter_by(id_personnel=current_user.id_personnel, id_campagne=campaign_id).first()

    
    
    if current_user.is_authenticated and not participation:
        try:
            new_participation = PARTICIPER_CAMPAGNE(id_personnel=current_user.id_personnel, id_campagne=campaign_id)
            db.session.add(new_participation)

            campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()
            campagne.participerCampagne.append(new_participation)
            db.session.commit()
            flash(f"Successfully enrolled in campaign")

        except OperationalError as e:
            db.session.rollback()
            flash(f"Database error occurred while enrolling in campaign: {e}", category="error")
    else:
        flash(f"You are already enrolled in this campaign for this period", category="info")

    return redirect(url_for("campaign_detail", campaign_id=campaign_id))



@app.route("/campaigns/<int:campaign_id>/disenroll/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.chercheur)
def disenroll_campaign(campaign_id: int):
    """
    Désinscrit l'utilisateur actuel d'une campagne spécifique.

    Args:
        campaign_id (int): L'identifiant de la campagne de laquelle se désinscrire.

    Returns:
        redirect: Redirige vers la page de détails de la campagne après la désinscription.
    """
    participation: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE.query.filter_by(id_personnel=current_user.id_personnel, id_campagne=campaign_id).first()

    if current_user.is_authenticated and participation:

        campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne=campaign_id).first()
        campagne.participerCampagne.remove(participation)
        db.session.delete(participation)
        db.session.commit()

        flash(f"Successfully disenrolled from campaign")
    else:
        flash(f"You are not enrolled in this campaign", category="info")

    return redirect(url_for("campaign_detail", campaign_id=campaign_id))



@app.route("/samples/")
@login_required
@role_access_rights(ROLE.chercheur)
def get_samples():
    """
    Affiche la page de présentation de l"ensembles des échantillons.

    Returns:
        str: Le rendu du template de la liste des échantillons.
    """

    page:int = request.args.get(key="page", default=1, type=int)
    samples : list[ECHANTILLON] = ECHANTILLON.query.all()

    shown_samples,page = _pagination(data= samples, page= page, items_per_page=5)
    
    return render_template("sample_dashboard.html",page=page, samples=shown_samples)


@app.route("/campaigns/<int:campaign_id>/samples/<int:sample_id>/", methods=["GET"])
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
    shown_samples,page = _pagination(data= samples, page= request.args.get(key="page",default=1,type=int), items_per_page=10)

    selected_sample:int = request.args.get(key="selected_sample",default=None,type=int)

    return render_template("sample_details.html", sample=sample, samples=shown_samples, page=page, selected_sample_id= selected_sample)



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
        try:
            form.create_sample(campaign_id= campaign_id)
            flash("Sample created successfully")
            return redirect(url_for("campaign_detail", campaign_id= campaign_id))
        except OperationalError as e:
            flash(e, category="error")
    
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

    print(form.validate_on_submit())
    print(form.errors)

    if form.validate_on_submit():
        try:
            form.update(sample_id= sample_id)
            flash("Sample updated successfully")
        except OperationalError as e:
            flash(e, category="error")

        return redirect(url_for("sample_detail", sample_id= sample_id, campaign_id= edit_sample.id_campagne))
    
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
    if sample is None:
        flash("Sample not found", category="error")
        return redirect(url_for("get_campaigns"))
    
    db.session.delete(sample)
    db.session.commit()
    flash(f"Sample ID {sample_id} deleted successfully")
    return redirect(url_for("campaign_detail", campaign_id= sample.id_campagne))



@app.route("/equipments/", methods=["GET","POST"])
@login_required
@role_access_rights(ROLE.technicien)
def get_equipments():
    """
    Affiche la page de gestion des équipements.

    Returns:
        str: Le rendu du template de gestion des équipements.
    """

    form: EquipmentForm = EquipmentForm()

    page: int = request.args.get(key="page", default=1, type=int)
    selected_equipment: int = request.args.get(key="selected_equipment", default=None, type=int)
    
    equipments: list[EQUIPEMENT] = EQUIPEMENT.query.all()
    equipments, page = _pagination(data= equipments, page= page)

    if form.validate_on_submit():
        if selected_equipment is not None:
            form.update(id_equipment= selected_equipment)
        else:
            form.create_equipment()

        return redirect(url_for('get_equipments', page=page, selected_equipment=selected_equipment))
    
    equipment_selected: EQUIPEMENT = EQUIPEMENT.query.filter_by(id_equipement= selected_equipment).first()

    if equipment_selected is not None:
        form.name.data = equipment_selected.nom_equipement
        form.submit.label.text = "Update"

        if equipment_selected.plateformes:
            form.plateform.data = equipment_selected.plateformes[0].nom_plateforme

        if equipment_selected.habilitations:
            form.habilitation.data = str(equipment_selected.habilitations[0].id_habilitation)

    return render_template("equipment_dashboard.html",form= form, page= page, equipments= equipments, selected_equipment= selected_equipment)



@app.route("/equipments/<int:id_equipment>/delete/")
@login_required
@role_access_rights(ROLE.technicien)
def delete_equipment(id_equipment: int) -> None:
    """
    Supprime un équipement existant.

    Args:
        id_equipment (int): L'identifiant de l'équipement à supprimer.

    Returns:
        redirect: Redirige vers la liste des équipements après la suppression.
    """
    equipment: EQUIPEMENT = EQUIPEMENT.query.get(id_equipment)
    if equipment:
        db.session.delete(equipment)
        db.session.commit()
        flash(f"Equipment deleted successfully")
    else:
        flash(f"Equipment ID {id_equipment} not found", category="error")

    print(f"Deleting Equipment ID: {id_equipment}")

    return redirect(url_for("get_equipments"))


  
@app.route('/gestion_personnel/', methods=['GET', 'POST'])
@login_required
@role_access_rights(ROLE.administratif)
def gestion_personnel():
    if request.method == 'POST':
        filtre = request.form.get('filtre')
    else:
        filtre = request.args.get('filtre')
    
    # On commence par une requête de base
    query = PERSONNEL.query

    # On applique le tri en fonction du filtre
    if filtre == 'nom':
        query = query.order_by(PERSONNEL.nom)
    elif filtre == 'prenom':
        query = query.order_by(PERSONNEL.prenom)
    elif filtre == 'role':
        query = query.order_by(PERSONNEL.role)
    else:
        # Tri par défaut si aucun filtre n'est sélectionné
        query = query.order_by(PERSONNEL.id_personnel)

    # On exécute la requête finale
    personnels = query.all()

    page = request.args.get('page', 1, type=int)
    personnels_paginated, page = _pagination(personnels, page)
    return render_template('personnel_administratif.html', personnels=personnels_paginated, page=page, filtre_actif=filtre)

@app.route('/gestion_personnel/add', methods=['POST'])
@login_required
@role_access_rights(ROLE.administratif)
def add_personnel():
    try:
        id_personnel_str = str(request.form.get('idPersonnel'))
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role_str = request.form.get('role')

        personnel_existant = PERSONNEL.query.filter_by(nom=nom, prenom=prenom, role=role_str).first()
        if nom == '' or prenom == '' or role_str == '':
            data = {
                'success': False,
                'message': 'Vous ne pouvez pas créer un personnel avec un nom vide, un prénom vide ou sans role, vous pouvez retourner en arrière'
            }
            json_response = json.dumps(data, indent=4, ensure_ascii=False)
            
            return Response(response=json_response,
                            status=400,
                            mimetype='application/json')
        if personnel_existant:
            data = {
                'success': False,
                'message': 'Un personnel avec ce nom, prénom et rôle existe déjà, vous pouvez retourner en arrière'
            }
            json_response = json.dumps(data, indent=4, ensure_ascii=False)
            
            return Response(response=json_response,
                            status=400,
                            mimetype='application/json')
 
        new_personnel = PERSONNEL(nom=nom,
                                prenom=prenom,
                                mdp = id_personnel_str+role_str[0],
                                role=role_str)
        
        db.session.add(new_personnel)
        db.session.commit()
        return redirect(url_for('gestion_personnel'))
    
    except Exception as e:
        db.session.rollback()
        data = {
            'success': False,
            'message': f'Erreur lors de la modification: {str(e)}'
        }
        json_response = json.dumps(data, indent=4, ensure_ascii=False)
            
        return Response(response=json_response,
                        status=400,
                        mimetype='application/json')

@app.route('/gestion_personnel/<int:id_personnel>/delete', methods=['POST'])
@login_required
@role_access_rights(ROLE.administratif)
def erase_personnel(id_personnel):
    personnel = db.session.get(PERSONNEL, id_personnel)

    if personnel:
        db.session.delete(personnel)
        db.session.commit()
    return redirect(url_for('gestion_personnel'))

@app.route('/gestion_personnel/edit/<int:id_personnel>', methods=['GET'])
def show_edit_form(id_personnel):
    personnel = db.session.get(PERSONNEL, id_personnel)
    if not personnel:
        return "Personnel non trouvé", 404
    return render_template('edit_personnel.html', personnel=personnel)

@app.route('/gestion_personnel/edit/<int:id_personnel>/', methods=['POST'])

@login_required
@role_access_rights(ROLE.administratif)
def edit_personnel(id_personnel):
    personnel = db.session.get(PERSONNEL, id_personnel)

    if personnel:
        try:
            personnel.nom = request.form.get('nom')
            personnel.prenom = request.form.get('prenom')
            personnel.role = request.form.get('role')
            new_mdp = request.form.get('mdp')
            if new_mdp:
                personnel.mdp = new_mdp
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la mise à jour : {e}")
            
    return redirect(url_for('gestion_personnel'))
  
  
  
def _pagination(data: list, page: int, items_per_page: int = 5) -> tuple[list,int]:
    """
    Pagine les données en fonction de la page et du nombre d"éléments par page.
    
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



def _budget_graph() -> None:
    """
    
    Produit le graphe représentant les budgets alloué
    et les budgets utilisé en fonction de leurs dates

    """
    
    # getting the data
    try:
        budgets: list[BUDGET] = BUDGET.query.order_by(BUDGET.date_mois_annee).all()

        if len(budgets) == 0:
            return

        used_budgets: list[float] = []
        for budget in budgets:
            used_budgets.append(budget.budget_total - db.session.query(func.remainingBudget(budget.date_mois_annee)).scalar())

        budgets_value: list[float] = [budget.budget_total for budget in budgets]
        dates: list[str] = [budget.date_mois_annee for budget in budgets]


        plt.figure(figsize=(10,6))
        plt.plot(dates, budgets_value, label= "total budget")
        plt.plot(dates, used_budgets,linestyle= "-.",label= "remaining budget",)

        plt.ylabel("Amount (€)")
        plt.xlabel("date")
        plt.legend()
        plt.savefig("LaboDino/static/image/budget_graph.png", format="png")
        plt.close()

    except Exception as e:
        print(e)
