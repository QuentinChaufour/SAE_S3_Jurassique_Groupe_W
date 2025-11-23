from LaboDino.forms import LoginForm, BudgetForm
from LaboDino.models import PERSONNEL, ROLE
from .app import app, db
from flask import render_template, jsonify, request, redirect, url_for, Response
import json

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

@app.route('/gestion_personnel/', methods=['GET', 'POST'])
def gestion_personnel():
    filtre = request.form.get('filtre')
    
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
        query = query.order_by(PERSONNEL.nom)

    # On exécute la requête finale
    personnels = query.all()
    
    return render_template('personnel_administratif.html', personnels=personnels, filtre_actif=filtre)

@app.route('/gestion_personnel/add', methods=['POST'])
def add_personnel():
    try:
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        role_str = request.form.get('role')

        personnel_existant = PERSONNEL.query.filter_by(nom=nom, prenom=prenom).first()
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
                'message': 'Un personnel avec ce nom et prénom existe déjà, vous pouvez retourner en arrière'
            }
            json_response = json.dumps(data, indent=4, ensure_ascii=False)
            
            return Response(response=json_response,
                            status=400,
                            mimetype='application/json')

        new_personnel = PERSONNEL(nom=nom,
                                prenom=prenom,
                                mdp = nom,
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
    
@app.route('/gestion_personnel/delete', methods=['POST'])
def erase_personnel():
    id_personnel = request.form.get("idPersonnel")
    personnel = PERSONNEL.query.get(id_personnel)

    if personnel:
        db.session.delete(personnel)
        db.session.commit()
    return redirect(url_for('gestion_personnel'))

# NOUVELLE ROUTE (GET) pour afficher la page de modification
@app.route('/gestion_personnel/edit/<int:idPersonnel>', methods=['GET'])
def show_edit_form(idPersonnel):
    personnel = PERSONNEL.query.get_or_404(idPersonnel)
    return render_template('edit_personnel.html', personnel=personnel)

# ROUTE MODIFIÉE (POST) pour traiter la modification
@app.route('/gestion_personnel/edit/<int:idPersonnel>', methods=['POST'])
def edit_personnel(idPersonnel):
    personnel = PERSONNEL.query.get(idPersonnel)

    if personnel:
        try:
            personnel.nom = request.form.get('nom')
            personnel.prenom = request.form.get('prenom')
            personnel.role = request.form.get('role')
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Gérer l'erreur, par exemple en affichant un message
            print(f"Erreur lors de la mise à jour : {e}")
            
    return redirect(url_for('gestion_personnel'))