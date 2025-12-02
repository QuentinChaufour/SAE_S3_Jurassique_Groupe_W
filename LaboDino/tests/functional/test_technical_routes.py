from LaboDino.models import PERSONNEL, PLATEFORME,EQUIPEMENT
from LaboDino.tests.conftest import testapp
from LaboDino.app import db
from datetime import date

def _get_technician(testapp) -> PERSONNEL:
    """Récupère un technicien"""
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom="Bernard", prenom="Luc", mdp="mdp789").first()

def login_technician(client, id: int, password: str, next: str):
    """Simule une connexion en tant que technicien"""
    data = {"id": id, "password": password}
    if next:
        data["next"] = next
        
    query_string = f"?next={next}" if next else ""
    return client.post(f"/login/{query_string}", data=data, follow_redirects=True)

def test_menu_technician_before_login(client):
    """Teste la connexion à la page de choix d'actions avant connexion"""
    response = client.get("/menu_technician/", follow_redirects=True)
    assert b"Login" in response.data

def test_menu_technician_after_login(client, testapp):
    """Teste la connexion à la page de choix d'actions après connexion"""
    with testapp.app_context():
        response = client.get("/menu_technician/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login/?next=%2Fmenu_technician%2F" in response.headers["Location"]

        technicien = _get_technician(testapp)
        response = login_technician(client, id=technicien.id_personnel, password="mdp789", next="/menu_technician/")
        assert response.status_code == 200
        assert b"Choix des actions" in response.data

def test_platform_management_before_login(client):
    """Teste la connexion à la page de gestion des plateformes avant connexion"""
    response = client.get("/menu_technician/platform_management/", follow_redirects=True)
    assert b"Login" in response.data

def test_platform_management_after_login(client, testapp):
    """Teste la connexion à la page de gestion des plateformes après connexion"""
    with testapp.app_context():
        response = client.get("/menu_technician/platform_management/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login/?next=%2Fmenu_technician%2Fplatform_management%2F" in response.headers["Location"]

        technicien = _get_technician(testapp)
        response = login_technician(client, id=technicien.id_personnel, password="mdp789", next="/menu_technician/platform_management/")
        assert response.status_code == 200
        assert b"Gestion des plateformes" in response.data
        assert "Créer une plateforme" in response.data.decode("utf-8")

def test_create_platform_success(client, testapp):
    """Teste la création de plateforme"""
    with testapp.app_context():
        technicien = _get_technician(testapp)
        login_technician(client, id=technicien.id_personnel, password="mdp789", next="/menu_technician/platform_management/")

        plateform = {
            "nom_plateforme": "Aristote",
            "nb_personnes_requises": 2,
            "cout_journalier": 500,
            "intervalle_maintenance": 30
        }

        response = client.post("/menu_technician/platform_management/", data=plateform, follow_redirects=True)

        assert response.status_code == 200
        assert b"Aristote" in response.data
        
        created_plat = PLATEFORME.query.filter_by(nom_plateforme="Aristote").first()
        assert created_plat is not None

        db.session.delete(created_plat)
        db.session.commit()

def test_delete_platform_success(client, testapp):
    """Teste la supression d'une plateforme"""
    with testapp.app_context():

        plateform = PLATEFORME(
            nom_plateforme="Aristote",
            nb_personnes_requises=2,
            cout_journalier=500,
            intervalle_maintenance=30
        )
        db.session.add(plateform)
        db.session.commit()

        technicien = _get_technician(testapp)
        login_technician(client, id=technicien.id_personnel, password="mdp789", next="/menu_technician/platform_management/")


        response = client.post("/menu_technician/platform_management/delete/", data={"nom_plateforme": "Aristote"}, follow_redirects=True)

        assert response.status_code == 200
        
        deleted = PLATEFORME.query.filter_by(nom_plateforme="Aristote").first()
        assert deleted is None
        if deleted is not None:
            db.session.delete(deleted)
            db.session.commit()

def test_update_platform_success(client, testapp):
    """Teste la modification d'une plateforme"""
    with testapp.app_context():
        name = "Plateforme Sequence"
        
        technicien = _get_technician(testapp)
        login_technician(client, id=technicien.id_personnel, password="mdp789", next=f"/menu_technician/platform_management/{name}/")

        update_data = {
            "nom_plateforme": name,
            "nb_personnes_requises": 10,
            "cout_journalier": 2000.0,
            "intervalle_maintenance": 120
        }

        response = client.post(f"/menu_technician/platform_management/{name}/", data=update_data, follow_redirects=True)

        assert response.status_code == 200
        
        updated_plat = PLATEFORME.query.filter_by(nom_plateforme=name).first()
        
        assert updated_plat.nb_personnes_requises == 10
        assert updated_plat.cout_journalier == 2000.0
        assert updated_plat.intervalle_maintenance == 120

def test_platform_sorting_complete(client, testapp):
    """Teste les options de tri"""
    with testapp.app_context():
        technicien = _get_technician(testapp)
        login_technician(client, id=technicien.id_personnel, password="mdp789", next="/menu_technician/platform_management/")

        response_nom = client.get("/menu_technician/platform_management/?filtre=nom", follow_redirects=True)
        assert response_nom.status_code == 200

        response_nb = client.get("/menu_technician/platform_management/?filtre=nb_personnes_requises", follow_redirects=True)
        assert response_nb.status_code == 200

        response = client.get("/menu_technician/platform_management/?filtre=cout_journalier", follow_redirects=True)
        assert response.status_code == 200



def _get_technician(testapp) -> PERSONNEL:
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom= "Bernard", prenom= "Luc", mdp="mdp789").first()



def test_equipment_dashboard_before_login(client, testapp):
    
    response = client.get("/equipments/", follow_redirects= True)
    assert b"Login" in response.data



def test_equipment_delete_before_login(client, testapp):
    response = client.get("/equipments/1/delete/", follow_redirects= True)
    assert b"Login" in response.data



def test_equipment_dashboard_after_login(client, testapp):
    with testapp.app_context():
         
        response = client.get("/equipments/", follow_redirects= True)
        assert b"Login" in response.data

        technician = _get_technician(testapp)
        login_technician(client, technician.id_personnel, "mdp789", "/equipments/")
        response = client.get("/equipments/", follow_redirects= True)
        assert b"ID" in response.data



def test_equipment_create_after_login(client, testapp):
    with testapp.app_context():
        
        response = client.get("/equipments/", follow_redirects= True)
        assert b"Login" in response.data

        technician = _get_technician(testapp)
        login_technician(client, technician.id_personnel, "mdp789", "/equipments/")

        response = client.post("/equipments/", data={
            "name": "Brush"
        }, follow_redirects= True)
        assert response.status_code == 200

        equipment: EQUIPEMENT = EQUIPEMENT.query.filter_by(nom_equipement="Brush").first()
        assert equipment is not None

        response = client.get("/equipments/?page=6", follow_redirects= True)
        assert b"Brush" in response.data

        db.session.delete(equipment)
        db.session.commit()



def test_equipment_delete_after_login(client, testapp):

    with testapp.app_context():

        equipment: EQUIPEMENT = EQUIPEMENT(nom_equipement="Hammer")
        db.session.add(equipment)
        db.session.commit()
        
        response = client.get("/equipments/1/delete/", follow_redirects= True)
        assert b"Login" in response.data

        technician = _get_technician(testapp)
        login_technician(client, technician.id_personnel, "mdp789", f"/equipments/")

        response = client.get(f"/equipments/{equipment.id_equipement}/delete/", follow_redirects= True)
        assert response.status_code == 200
        print(response.data)
        assert b"Equipment deleted successfully" in response.data
