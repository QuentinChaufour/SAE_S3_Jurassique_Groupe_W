from .app import app, db
from .decorators import role_access_rights
from flask import render_template,redirect, url_for, request, redirect, url_for, Response
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, BudgetForm, PlatformForm
from .models import PERSONNEL, ROLE, PLATEFORME
from sqlalchemy.exc import OperationalError
import json

@app.route("/")
def home():
    return redirect(url_for("login"))

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
        un_user = form.authenticate()
        if un_user:
            login_user(un_user)
            
            if form.next.data:
                next_page = form.next.data
            else:
                user_role = un_user.get_role()
                match user_role:
                    case ROLE.chercheur:
                        next_page = url_for("get_campaigns")
                    case ROLE.technicien:
                        next_page = url_for("menu_technician")
                    case ROLE.direction:
                        next_page = url_for("set_budget")
                    case ROLE.administratif:
                        next_page = url_for("gestion_personnel")
                    case default:
                        next_page = url_for("login")
            
            return redirect(next_page)
        else:
            # Failed login logic here
            print("Authentication failed")

    print(form.id.data)
    print(form.password.data)
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
        try:
            platform = PLATEFORME(
                nom_plateforme=form.nom_plateforme.data,
                nb_personnes_requises=form.nb_personnes_requises.data,
                cout_journalier=form.cout_journalier.data,
                intervalle_maintenance=form.intervalle_maintenance.data
            )
            db.session.add(platform)
            print(platform)
            db.session.commit()
        except OperationalError as e:
            print(f"Database error occurred while creating platform: {e}")

        return redirect(url_for('platform_management', filtre=filtre))
    
    data = query.all()  

    page = request.args.get('page', 1, type=int)
    return render_template('platform_management.html', form=form, platforms= _pagination(data, page), page= page, filtre_actif=filtre)

@app.route("/menu_technician/platform_management/<string:platform_name>/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.technicien)
def platform_detail(platform_name):

    form = PlatformForm()
    if form.validate_on_submit():
        platforms_name = [plateforme.nom_plateforme for plateforme in PLATEFORME.query.all()]
        if form.nom_plateforme.data in platforms_name:
            platform = PLATEFORME.query.filter_by(nom_plateforme=form.nom_plateforme.data).first()
            print("PLATEFORME ", PLATEFORME.query.filter_by(nom_plateforme=form.nom_plateforme.data).first())
            platform.nb_personnes_requises = form.nb_personnes_requises.data
            platform.cout_journalier = form.cout_journalier.data
            platform.intervalle_maintenance = form.intervalle_maintenance.data
            print(platform)
            db.session.commit()
            return redirect(url_for('platform_detail', platform_name=form.nom_plateforme.data))

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

@login_required
@app.route("/campaigns/", methods=["GET", "POST"])
@role_access_rights(ROLE.chercheur)
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
@role_access_rights(ROLE.chercheur)
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
@role_access_rights(ROLE.chercheur)
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
