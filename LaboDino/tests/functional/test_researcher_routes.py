from datetime import date
from LaboDino.models import PARTICIPER_CAMPAGNE, PERSONNEL,CAMPAGNE
from LaboDino.app import db

# Fonction de récupération des PK a cause des autos-increment ---------

def _get_researcher(testapp) -> PERSONNEL:
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom= "Martin", prenom= "Sophie", mdp="mdp456").first()



def _get_campaign_id(testapp) -> int:
    with testapp.app_context():
        return CAMPAGNE.query.filter_by(nom_plateforme= "Plateforme Analyse",lieu= "Gobi, Mongolie", dateDebut= date(2024, 6, 1)).first().id_campagne


def _get_sample_id(testapp) -> int:
    with testapp.app_context():
        campagne = CAMPAGNE.query.filter_by(nom_plateforme= "Plateforme Analyse",lieu= "Gobi, Mongolie", dateDebut= date(2024, 6, 1)).first()
        return campagne.echantillons[0].id_echantillon



def login_researcher(client, id: int, password: str, next: str):

    query_string = f"?next={next}" if next else ""

    return client.post(f"/login/{query_string}", data={"id": id,"password": password}, follow_redirects= True)

# ----------------------------------------------------------------------

def test_campaigns_dashboard_before_login(client):
    response = client.get("/campaigns/", follow_redirects= True)
    assert b"Login" in response.data



def test_create_campaign_before_login(client):
    response = client.get("/campaigns/create/", follow_redirects= True)
    assert b"Login" in response.data



def test_edit_campaign_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.get(f"/campaigns/{campaign}/edit/", follow_redirects= True)
    assert b"Login" in response.data



def test_delete_campaign_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.post(f"/campaigns/{campaign}/delete/", follow_redirects= True)
    assert b"Login" in response.data



def test_campaign_detail_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.get(f"/campaigns/{campaign}/", follow_redirects= True)
    assert b"Login" in response.data



def test_campaign_enrollment_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.post(f"/campaigns/{campaign}/enroll/", follow_redirects= True)
    assert b"Login" in response.data



def test_campaign_unenrollment_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.post(f"/campaigns/{campaign}/disenroll/", follow_redirects= True)
    assert b"Login" in response.data



def test_sample_dashboard_before_login(client):
    pass



def test_sample_detail_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)
    sample:int = _get_sample_id(testapp)

    response = client.get(f"/campaigns/{campaign}/samples/{sample}/", follow_redirects= True)
    assert b"Login" in response.data



def test_sample_edit_before_login(client, testapp):
    sample:int = _get_sample_id(testapp)

    response = client.post(f"/campaigns/samples/{sample}/edit/", follow_redirects= True)
    assert b"Login" in response.data 



def test_sample_create_before_login(client, testapp):
    campaign:int = _get_campaign_id(testapp)

    response = client.post(f"/campaigns/{campaign}/samples/create/", follow_redirects= True)
    assert b"Login" in response.data



def test_sample_delete_before_login(client, testapp):
    sample:int = _get_sample_id(testapp)

    response = client.post(f"/campaigns/samples/{sample}/delete/", follow_redirects= True)
    assert b"Login" in response.data



def test_campaigns_dashboard_after_login(client, testapp):
    with testapp.app_context():
        # User non connecté
        response = client.get("/campaigns/", follow_redirects= False)
        assert response.status_code == 302

        assert "/login/?next=%2Fcampaigns%2F" in response.headers["Location"]

        # User connecté
        chercheur = _get_researcher(testapp)
        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next="/campaigns/?page=3")
        assert response.status_code == 200
        assert b"Montana, USA" in response.data

        response = client.get("/campaigns/?page=2&completed=True", follow_redirects= False)
        assert b"Montana, USA" in response.data

        response = client.get("/campaigns/?page=2&completed=False", follow_redirects= False)
        assert b"Montana, USA" not in response.data



def test_create_campaign_after_login(client, testapp):
    with testapp.app_context():
        response = client.get("/campaigns/create/", follow_redirects= False)
        assert response.status_code == 302

        assert "/login/?next=%2Fcampaigns%2Fcreate%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next="/campaigns/create/")
        assert response.status_code == 200
        assert b"Create a Campaign" in response.data

        assert client.post(
            "/campaigns/create/",
            data={
                "plateforme": "Plateforme A",
                "lieu": "Test Land",
                "startDate": "2024-02-01",
                "duree": 15,
                "participate": "false"
            },
            follow_redirects=True,
        ).status_code == 200

        response = client.get("/campaigns/?page=3", follow_redirects= True)
        print(response.data)
        assert b"Test Land" in response.data

        assert client.post(
            "/campaigns/create/",
            data={
                "plateforme": "Plateforme B",
                "lieu": "Test Land B",
                "startDate": "2024-02-01",
                "duree": 5,
                "participate": "on"
            },
            follow_redirects=True,
        ).status_code == 200

        response = client.get("/campaigns/?page=3", follow_redirects= True)
        print(response.data)
        assert b"Test Land B" in response.data
        camp = CAMPAGNE.query.filter_by(nom_plateforme= "Plateforme B",lieu= "Test Land B", dateDebut= date(2024, 2, 1)).first()
        print(camp.participerCampagne)

        assert chercheur.id_personnel == camp.participerCampagne[0].id_personnel

        # Clean up the created campaigns
        with testapp.app_context():
            camp1 = CAMPAGNE.query.filter_by(nom_plateforme= "Plateforme A",lieu= "Test Land", dateDebut= date(2024, 2, 1)).first()
            camp2 = CAMPAGNE.query.filter_by(nom_plateforme= "Plateforme B",lieu= "Test Land B", dateDebut= date(2024, 2, 1)).first()
            part = PARTICIPER_CAMPAGNE.query.filter_by(id_campagne= camp2.id_campagne, id_personnel= chercheur.id_personnel).first()

            db.session.delete(part)
            db.session.delete(camp1)
            db.session.delete(camp2)
            db.session.commit()



def test_edit_campaign_after_login(client, testapp):
    pass



def test_delete_campaign_after_login(client, testapp):
    pass



def test_campaign_detail_page_after_login(client, testapp):
    pass



def test_campaign_enrollment_after_login(client, testapp):
    pass



def test_campaign_unenrollment_after_login(client, testapp):
    pass



def test_sample_dashboard_after_login(client, testapp):
    pass



def test_sample_detail_after_login(client, testapp):
    pass



def test_sample_create_after_login(client, testapp):
    pass



def test_sample_edit_after_login(client, testapp):
    pass



def test_sample_delete_after_login(client, testapp):
    pass