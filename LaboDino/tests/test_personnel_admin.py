import pytest
from LaboDino.app import app, db
from LaboDino.models import PERSONNEL, ROLE
import config
import os
from bs4 import BeautifulSoup

@pytest.fixture
def testapp():
    app.config.update({"TESTING":True,"SQLALCHEMY_DATABASE_URI":
    'mysql://moins:moins@servinfo-maria/DBmoins',"WTF_CSRF_ENABLED": False})
    with app.app_context():
        pass
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
    # --- SETUP : Créer un utilisateur à supprimer ---
    personnel_a_supprimer = PERSONNEL(nom='ASupprimer', prenom='Test', mdp='temp', role=ROLE.chercheur)
    with app.app_context():
        db.session.add(personnel_a_supprimer)
        db.session.commit()

        id_a_supprimer = personnel_a_supprimer.id_personnel

    client.post('/login/', data={'id': '16', 'password': 'MM@34'}, follow_redirects=True)

    # Appeler la bonne URL pour la suppression
    response_delete = client.post(f'/gestion_personnel/{id_a_supprimer}/delete', follow_redirects=True)

    assert response_delete.status_code == 200
    assert b'Gestion du personnel' in response_delete.data

    assert b'ASupprimer' not in response_delete.data
