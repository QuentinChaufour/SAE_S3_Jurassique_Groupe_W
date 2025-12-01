from datetime import date
from LaboDino.models import ECHANTILLON, PARTICIPER_CAMPAGNE, PERSONNEL,CAMPAGNE
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
    response = client.get("/samples/", follow_redirects= True)
    assert b"Login" in response.data



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



def test_species_create_before_login(client):
    pass



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
    
    with testapp.app_context():

        campaign:int = _get_campaign_id(testapp)

        response = client.get(f"/campaigns/{campaign}/edit/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2Fedit%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/edit/")
        assert response.status_code == 200
        assert b"Edit a Campaign" in response.data

        response = client.post(
            f"/campaigns/{campaign}/edit/",
            data={
                "plateforme": "Plateforme Analyse",
                "lieu": "Lieu Modifie",
                "startDate": "2024-06-01",
                "duree": 20,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Lieu Modifie" in response.data



def test_delete_campaign_after_login(client, testapp):
    with testapp.app_context():

        campaign:CAMPAGNE = CAMPAGNE(nom_plateforme= "Plateforme A", lieu= "Lieu Suppr", dateDebut= date(2024, 1, 1), duree= 10)
        db.session.add(campaign)
        db.session.commit()

        response = client.post(f"/campaigns/{campaign.id_campagne}/delete/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign.id_campagne}%2Fdelete%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign.id_campagne}/delete/")
        assert response.status_code == 200

        response = client.get("/campaigns/?page=3", follow_redirects= True)
        assert b"Lieu Suppr" not in response.data



def test_campaign_detail_page_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)

        response = client.get(f"/campaigns/{campaign}/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/")
        assert response.status_code == 200
        assert b"Gobi, Mongolie" in response.data



def test_campaign_enrollment_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)

        response = client.get(f"/campaigns/{campaign}/enroll/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2Fenroll%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/enroll/")
        assert response.status_code == 200
        print(response.data)
        campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne= campaign).first()
        participations = [part.id_personnel for part in campagne.participerCampagne]
        print(participations)
        assert b"Martin Sophie" in response.data


        assert chercheur.id_personnel in participations

        participation: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE.query.filter_by(id_campagne= campaign, id_personnel= chercheur.id_personnel).first()
        campagne.participerCampagne.remove(participation)
        db.session.delete(participation)
        db.session.commit()


def test_campaign_unenrollment_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)
        campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne= campaign).first()
        chercheur: PERSONNEL = _get_researcher(testapp)
        participation: PARTICIPER_CAMPAGNE = PARTICIPER_CAMPAGNE(id_personnel= _get_researcher(testapp).id_personnel, id_campagne= campaign)
        campagne.participerCampagne.append(participation)
        db.session.add(participation)
        db.session.commit()

        response = client.get(f"/campaigns/{campaign}/disenroll/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2Fdisenroll%2F" in response.headers["Location"]
        # User connecté

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/disenroll/")
        assert response.status_code == 200

        campagne: CAMPAGNE = CAMPAGNE.query.filter_by(id_campagne= campaign).first()
        participations = [part.id_personnel for part in campagne.participerCampagne]

        assert b"Martin Sophie" not in response.data
        assert chercheur.id_personnel not in participations



def test_sample_dashboard_after_login(client, testapp):
    
    with testapp.app_context():
        # User non connecté
        response = client.get("/samples/", follow_redirects= False)
        assert response.status_code == 302

        assert "/login/?next=%2Fsamples%2F" in response.headers["Location"]

        # User connecté
        chercheur = _get_researcher(testapp)
        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next="/samples/")
        assert response.status_code == 200
        assert b"Tyrannosaurus" in response.data



def test_sample_detail_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)
        sample:int = _get_sample_id(testapp)

        response = client.get(f"/campaigns/{campaign}/samples/{sample}/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2Fsamples%2F{sample}%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/samples/{sample}/")
        assert response.status_code == 200
        assert b"Vertebre de sauropode" in response.data



def test_sample_create_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)

        response = client.get(f"/campaigns/{campaign}/samples/create/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2F{campaign}%2Fsamples%2Fcreate%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)

        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/{campaign}/samples/create/")
        assert response.status_code == 200
        assert b"Create a Sample" in response.data

        response = client.post(
            f"/campaigns/{campaign}/samples/create/",
            data={
                "dna_file": "./tests/functional/test.adn",
                "comment": "Os de dinosaure",
                "specie": ""
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Os de dinosaure" in response.data

        echantillon: ECHANTILLON = ECHANTILLON.query.filter_by(id_campagne= campaign, commentaire= "Os de dinosaure").first()
        db.session.delete(echantillon)
        db.session.commit()

def test_sample_edit_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)
        echantillon: ECHANTILLON = ECHANTILLON(id_campagne= campaign, fichier_sequence_adn= "./tests/functional/test.adn", commentaire= "Os de dinosaure")
        print(echantillon)
        db.session.add(echantillon)
        db.session.commit()

        response = client.get(f"/campaigns/samples/{echantillon.id_echantillon}/edit/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2Fsamples%2F{echantillon.id_echantillon}%2Fedit%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)
        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456", next=f"")
        assert response.status_code == 200

        response = client.post(
            f"/campaigns/samples/{echantillon.id_echantillon}/edit/",
            data={
                "dna_file": echantillon.fichier_sequence_adn,
                "comment": "Os de dinosaure modifie",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        print(response.data)
        assert b"Os de dinosaure modifie" in response.data

        print(ECHANTILLON.query.all())
        echantillon: ECHANTILLON = ECHANTILLON.query.filter_by(id_echantillon= echantillon.id_echantillon).first()
        db.session.delete(echantillon)
        db.session.commit()

def test_sample_delete_after_login(client, testapp):
    with testapp.app_context():
        campaign:int = _get_campaign_id(testapp)
        echantillon: ECHANTILLON = ECHANTILLON(id_campagne= campaign, fichier_sequence_adn= "./tests/functional/test.adn", commentaire= "Os de dinosaure")
        db.session.add(echantillon)
        db.session.commit()

        response = client.post(f"/campaigns/samples/{echantillon.id_echantillon}/delete/", follow_redirects= False)
        assert response.status_code == 302

        assert f"/login/?next=%2Fcampaigns%2Fsamples%2F{echantillon.id_echantillon}%2Fdelete%2F" in response.headers["Location"]
        # User connecté
        chercheur: PERSONNEL = _get_researcher(testapp)
        response = login_researcher(client, id=chercheur.id_personnel, password="mdp456",next=f"/campaigns/samples/{echantillon.id_echantillon}/delete/")
        assert response.status_code == 200
        assert b"Os de dinosaure" not in response.data