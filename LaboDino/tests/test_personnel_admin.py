import pytest
from LaboDino.app import app, db
from LaboDino.models import PERSONNEL, ROLE
import config
import os
from bs4 import BeautifulSoup

@pytest.fixture
def testapp():
    app.config.update({"TESTING":True,"SQLALCHEMY_DATABASE_URI":
    'mysql://root:moins@127.0.0.1/LaboDino',"WTF_CSRF_ENABLED": False})
    yield app

@pytest.fixture
def client(testapp):
    return testapp.test_client()

def test_gestion_personnel_get_with_filter(client):
    """
    Test: -Filtrage par nom
          -Filtrage par prénom
          -Filtrage par rôle
    """
    client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)

    response = client.get('/gestion_personnel/?filtre=nom')

    assert response.status_code == 200

    # Analyser le HTML de la réponse
    soup = BeautifulSoup(response.data, 'html.parser')

    # Trouver la première ligne (tr) dans le corps de la table (tbody)
    table_body = soup.find('table', {'id': 'table-admin'}).find('tbody')
    first_row = table_body.find('tr')

    # Extraire les cellules (td) de cette première ligne
    cells = first_row.find_all('td')
    # Vérifier le contenu de la première cellule (le nom)
    # text.strip(): nettoie le texte des espaces superflus
    first_personnel_nom = cells[0].text.strip()
    
    assert first_personnel_nom == 'Belobog'


    response = client.get('/gestion_personnel/?filtre=prenom')

    soup = BeautifulSoup(response.data, 'html.parser')

    table_body = soup.find('table', {'id': 'table-admin'}).find('tbody')
    first_row = table_body.find('tr')

    cells = first_row.find_all('td')
    first_personnel_prenom = cells[1].text.strip()
    
    assert first_personnel_prenom == 'Alexandrina'


    response = client.post('/gestion_personnel/', data={'filtre': 'role'})

    soup = BeautifulSoup(response.data, 'html.parser')

    table_body = soup.find('table', {'id': 'table-admin'}).find('tbody')
    first_row = table_body.find('tr')

    cells = first_row.find_all('td')
    first_personnel_prenom = cells[2].text.strip()
    
    assert first_personnel_prenom == 'administratif'

def test_erase_personnel(client):
    personnel_a_supprimer = PERSONNEL(nom='ASupprimer', prenom='Test', mdp='t_erase', role=ROLE.chercheur)
    id_a_supprimer = None
    try:
        with app.app_context():
            db.session.add(personnel_a_supprimer)
            db.session.commit()
            id_a_supprimer = personnel_a_supprimer.id_personnel

        client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)
        response_delete = client.post(f'/gestion_personnel/{id_a_supprimer}/delete', follow_redirects=True)

        assert response_delete.status_code == 200
        assert b'ASupprimer' not in response_delete.data
    finally:
        if id_a_supprimer:
            with app.app_context():
                user = db.session.get(PERSONNEL, id_a_supprimer)
                if user:
                    db.session.delete(user)
                    db.session.commit()

def test_edit_personnel(client):
    personnel_a_modifier = PERSONNEL(nom='OriginalNom', prenom='OriginalPrenom', mdp='t_edit', role=ROLE.technicien)
    id_a_modifier = None
    try:
        with app.app_context():
            db.session.add(personnel_a_modifier)
            db.session.commit()
            id_a_modifier = personnel_a_modifier.id_personnel

        client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)
        response = client.post(
            f'/gestion_personnel/edit/{id_a_modifier}', 
            data={'nom': 'NouveauNom', 'prenom': 'NouveauPrenom', 'role': 'chercheur'},
            follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            personnel_modifie = db.session.get(PERSONNEL, id_a_modifier)
            assert personnel_modifie.nom == 'NouveauNom'
            assert personnel_modifie.role == ROLE.chercheur
    finally:
        if id_a_modifier:
            with app.app_context():
                user = db.session.get(PERSONNEL, id_a_modifier)
                if user:
                    db.session.delete(user)
                    db.session.commit()

def test_edit_personnel_fails_on_unique_constraint(client):
    user_to_edit = PERSONNEL(nom='CibleNom', prenom='CiblePrenom', mdp='mdp1', role=ROLE.technicien)
    blocking_user = PERSONNEL(nom='Bloqueur', prenom='Test', mdp='mdp2', role=ROLE.chercheur)
    id_to_edit, id_to_block = None, None
    try:
        with app.app_context():
            db.session.add_all([user_to_edit, blocking_user])
            db.session.commit()
            id_to_edit = user_to_edit.id_personnel
            id_to_block = blocking_user.id_personnel

        client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)

        client.post(
            f'/gestion_personnel/edit/{id_to_edit}', 
            data={'nom': 'Echec', 'prenom': 'Echec', 'role': 'chercheur', 'mdp': 'mdp2'},
            follow_redirects=True
        )

        with app.app_context():
            personnel_apres_echec = db.session.get(PERSONNEL, id_to_edit)
            assert personnel_apres_echec.nom == 'CibleNom'
    finally:
        with app.app_context():
            if id_to_edit:
                u1 = db.session.get(PERSONNEL, id_to_edit)
                if u1: db.session.delete(u1)
            if id_to_block:
                u2 = db.session.get(PERSONNEL, id_to_block)
                if u2: db.session.delete(u2)
            db.session.commit()

def test_show_edit_form(client):
    """
    Teste que la page de modification s'affiche correctement
    avec les bonnes informations pré-remplies.
    """
    personnel = PERSONNEL(nom='TestNom', prenom='TestPrenom', mdp='t_show', role=ROLE.technicien)
    id_personnel = None
    try:
        with app.app_context():
            db.session.add(personnel)
            db.session.commit()
            id_personnel = personnel.id_personnel
        
        client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)
        
        response = client.get(f'/gestion_personnel/edit/{id_personnel}')
        
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        nom_input = soup.find('input', {'name': 'nom'})
        prenom_input = soup.find('input', {'name': 'prenom'})
        role_selected_option = soup.find('select', {'name': 'role'}).find('option', selected=True)

        assert nom_input['value'] == 'TestNom'
        assert prenom_input['value'] == 'TestPrenom'
        assert role_selected_option['value'] == 'technicien'

    finally:
        if id_personnel:
            with app.app_context():
                user = db.session.get(PERSONNEL, id_personnel)
                if user:
                    db.session.delete(user)
                    db.session.commit()



