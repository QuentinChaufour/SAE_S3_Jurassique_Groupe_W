from .forms import LoginForm, BudgetForm, PlatformForm, MaintenanceForm
from .app import app, db
from .decorators import role_access_rights
from .models import PERSONNEL, ROLE, PLATEFORME, MAINTENANCE
from flask import flash, render_template,redirect, url_for,request
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date

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
            login_user(unUser)
            
            if form.next.data:
                next_page = form.next.data
            else:
                user_role = unUser.get_role()
                match user_role:
                    case ROLE.chercheur:
                        next_page = url_for("get_campaigns")
                    case ROLE.technicien:
                        next_page = url_for("menu_technician")
                    case ROLE.direction:
                        next_page = url_for("set_budget")
                    case ROLE.administratif:
                        #TODO need to have the admin page in order to put the redirection
                        next_page = url_for("login")
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
    form.create_platform(filtre)
    
    data = query.all()  

    page = request.args.get('page', 1, type=int)
    return render_template('platform_management.html', form=form, platforms= _pagination(data, page), page= page, filtre_actif=filtre)

@app.route("/menu_technician/platform_management/<string:platform_name>/", methods=["GET", "POST"])
@login_required
@role_access_rights(ROLE.technicien)
def platform_detail(platform_name):

    form = PlatformForm()
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

    form.create_maintenance(filtre)
    
    data = query.all()  
    page = request.args.get('page', 1, type=int)

    return render_template('maintenance_management.html', form=form, maintenances= _pagination(data, page), page= page, filtre_actif=filtre)

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
    return render_template("campaign_details.html", campaign_id=campaign_id, samples= [1,2],participants= {1:["a","b","c"],2:["d","e"]})

@app.route("/campaigns/samples/<int:sample_id>")
@login_required
def sample_detail(sample_id: int):
    """Affiche les détails d"un échantillon spécifique."""
    # Logic to retrieve and display sample details
    print(f"Sample ID: {sample_id}")
    return render_template("sample_details.html", sample=sample_id, samples= [1,2,3,4])

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
  
