from LaboDino.models import PERSONNEL, EQUIPEMENT
from LaboDino.app import db
from datetime import date


def _get_technician(testapp) -> PERSONNEL:
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom= "Bernard", prenom= "Luc", mdp="mdp789").first()



def login_technician(client, id: int, password: str, next: str):

    query_string = f"?next={next}" if next else ""
    return client.post(f"/login/{query_string}", data={"id": id,"password": password}, follow_redirects= True)
    


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