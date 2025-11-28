
def login_researcher(client, id: int, password: str, next: str):
    return client.post("/login/" + next, data={"id": id,"password": password}, follow_redirects= True)

def test_campaigns_dashboard_before_login(client):
    response = client.get("/campaigns/", follow_redirects= True)
    assert b"Login" in response.data

def test_campaigns_dashboard_after_login(client, testapp):
    # User non connecté
    response = client.get("/campaigns/", follow_redirects= False)
    assert response.status_code == 302

    assert "/login/?next=%2Fcampaigns%2F" in response.headers["Location"]

    response = login_researcher(client, 2, "mdp456","?next=%2Fcampaigns%2F/?page=2")
    assert response.status_code == 200

    print(response.data)
    assert b"Montana, USA" in response.data
    