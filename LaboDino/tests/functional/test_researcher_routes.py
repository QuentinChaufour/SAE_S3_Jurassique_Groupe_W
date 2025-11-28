from LaboDino.models import PERSONNEL
from LaboDino.tests.conftest import testapp

def _get_researcher(testapp) -> PERSONNEL:
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom= "Martin", prenom= "Sophie", mdp="mdp456").first()

def login_researcher(client, id: int, password: str, next: str):

    query_string = f"?next={next}" if next else ""

    return client.post(f"/login/{query_string}", data={"id": id,"password": password}, follow_redirects= True)
    
def test_campaigns_dashboard_before_login(client):
    response = client.get("/campaigns/", follow_redirects= True)
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
    