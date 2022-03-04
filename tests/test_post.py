import json

# import pytest
# from tests.confest import test_app
# from fastapi.testclient import TestClient

# def test_create_note(test_app, monkeypatch):
#     test_request_payload = {"title": "something", "description": "something else"}
#     test_response_payload = {"id": 1, "title": "something", "description": "something else"}

#     async def mock_post(payload):
#         return 1
#     # monkeypatch.setattr(crud, "post", mock_post)
#     response = TestClient().get("http://127.0.0.1:8000/auth/users/")
#     print ('>>>>>>>>>>>')
#     print (response)
#     # response = test_app.post("/posts/", data=json.dumps(test_request_payload),)

#     assert response.status_code == 201
#     assert response.json() == test_response_payload

import pytest
from httpx import AsyncClient

from main import app, SECRET_KEY

DOMAIN_IP = 'http://127.0.0.1:8000'

@pytest.mark.anyio
async def test_post():
    
    ###### Create Post #############
    test_request_payload = {
        "name": "something Newwwwwwwwwww", 
        "title": "something else", 
        "author": "azarmhmd21@gmail.com",
        "stock_page" : [{"_id": "8a3553a4-0952-43e3-a8d5-cd7ae3075f2c"}]
    }

    test_mock_response = {'name': 'something Newwwwwwwwwww', 'title': 'something else', 'author': 'azarmhmd21@gmail.com', 'comments': [], 'spoilers_enabled': False, 'created_utc': '2022-02-08T19:09:49.833137', 'distinguished': False, 'stock_page': [{'_id': '8a3553a4-0952-43e3-a8d5-cd7ae3075f2c'}], 'has_edited': False, 'is_original_content': True, 'has_locked': False, 'has_saved': True, 'has_stickied': False, 'num_comments': 0, 'up_vote': 0, 'down_vote': 0, 'total_votes': 0, 'url': '', 'selftext': '', 'has_draft': False, 'flairs': [], 'image': None, 'link': None}
    
    files = {
        'post': json.dumps(test_request_payload),
        'Content-Disposition': 'form-data;',
        'Content-Type': 'multipart/form-data'
    }
    async with AsyncClient() as client:
        response = await client.post(DOMAIN_IP + '/posts/create', data=files)
    post_json = response.json()
    post_id = None
    if post_json:
        post_id = post_json['_id']
        del post_json['_id']
    print (post_json)
    assert response.status_code == 200
    

    ###### Update Post #############
    update_post_url = '/posts/' + post_id
    payload = {
        "title": "Updated Post title",
        "name": "Updated Post description",
        "author": "azarmhmd21@gmail.com",
        "stock_page" : [{"_id": "8a3553a4-0952-43e3-a8d5-cd7ae3075f2c"}]
    }

    response_payload = {'name': 'Updated Post description', 'title': 'Updated Post title', 'spoilers_enabled': False, 'distinguished': False, 'has_edited': False, 'is_original_content': True, 'has_locked': False, 'has_saved': True, 'has_stickied': False, 'url': '', 'selftext': '', 'has_draft': False, 'flairs': [], 'image': None, 'link': None}
    
    async with AsyncClient() as client:
        response = await client.put(DOMAIN_IP + update_post_url, data=json.dumps(payload))
    print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print (response.json())
    assert response.status_code in [200, 201]
    assert response.json() == response_payload

    ###### Bookamrk Post #############
    bookmark_url = '/posts/' + post_id + '/bookmark/'
    payload = {
        "email": "user@example.com"
    }
    print (DOMAIN_IP + bookmark_url)
    files = {
        'email': "user@example.com",
        'Content-Type': 'application/json'
    }
    async with AsyncClient() as client:
        response = await client.patch(DOMAIN_IP + bookmark_url, data=json.dumps(payload))
    print (response.json())
    assert response.status_code == 201
    assert response.json() == "Post has been bookmarked."


    ###### Un-Bookamrk Post #############
    un_bookmark_url = '/posts/' + post_id + '/un-bookmark/'
    payload = {
        "email": "user@example.com"
    }
    async with AsyncClient() as client:
        response = await client.patch(DOMAIN_IP + un_bookmark_url, data=json.dumps(payload))
    assert response.status_code == 201
    assert response.json() == "Bookamrked Post has been un-bookmarked."

    ###### Vote Post Up/Down Vote #############
    up_vote_post = '/posts/' + post_id + '/vote?vote_type=up'
    
    async with AsyncClient() as client:
        response = await client.patch(DOMAIN_IP + up_vote_post)
    print(response.json())
    assert response.status_code == 201
    
    assert response.json() == "Succefully Updated the Vote"

    down_vote_post = '/posts/' + post_id + '/vote?vote_type=down'
    
    async with AsyncClient() as client:
        response = await client.patch(DOMAIN_IP + down_vote_post)
    print(response.json())
    assert response.status_code == 201
    
    assert response.json() == "Succefully Updated the Vote"



