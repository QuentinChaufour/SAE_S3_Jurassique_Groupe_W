from LaboDino.models import PERSONNEL, BUDGET
from LaboDino.app import db
from datetime import date


def _get_director(testapp) -> PERSONNEL:
    with testapp.app_context():
        return PERSONNEL.query.filter_by(nom= "Dubois", prenom= "Marie", mdp="mdp101").first()



def login_researcher(client, id: int, password: str, next: str):

    query_string = f"?next={next}" if next else ""
    return client.post(f"/login/{query_string}", data={"id": id,"password": password}, follow_redirects= True)
    


def test_budget_creation_before_login(client, testapp):
    
    response = client.get("/budget/", follow_redirects= True)
    assert b"Login" in response.data



def test_budget_creation_after_login(client, testapp):
    with testapp.app_context():
        director = _get_director(testapp)
        response = login_researcher(client, director.id_personnel, "mdp101", next="/budget/")
        assert b"Fixer le budget mensuel" in response.data

        response = client.post("/budget/",
                              data={
                                  "date": "2023-10-01",
                                  "montant": 10500
                              },
                              follow_redirects= True)
        
        budget: BUDGET = BUDGET.query.filter_by(date_mois_annee="2023-10-01").first()
        assert budget is not None
        assert budget.budget_total == 10500

        db.session.delete(budget)
        db.session.commit()



def test_budget_modification_after_login(client, testapp):
    with testapp.app_context():
        director = _get_director(testapp)
        response = login_researcher(client, director.id_personnel, "mdp101", next="/budget/")
        assert b"Fixer le budget mensuel" in response.data

        # Create initial budget
        budget = BUDGET(date_mois_annee= date(2026, 11, 1), budget_total= 8000)
        db.session.add(budget)
        db.session.commit()

        # Modify the budget
        response = client.post("/budget/",
                              data={
                                  "date": "2026-11-01",
                                  "montant": 12000
                              },
                              follow_redirects= True)
        
        modified_budget: BUDGET = BUDGET.query.filter_by(date_mois_annee="2026-11-01").first()
        assert modified_budget is not None
        assert modified_budget.budget_total == 12000

        db.session.delete(modified_budget)
        db.session.commit()
        