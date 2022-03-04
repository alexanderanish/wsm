from tests.confest import test_app

def test_ping(test_app):
    response = test_app.get("/list-users/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}