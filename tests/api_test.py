import time
import requests


def wait_for_http(url):
    retries = 100
    exception = None
    while retries > 0:
        try:
            requests.get(url)
            return
        except requests.exceptions.ConnectionError as e:
            exception = e
            print(f'Got ConnectionError for url {url}: {e} , retrying')
            retries -= 1
            time.sleep(2)
    raise exception


task_service_url = 'http://127.0.0.1:8000'
wait_for_http(task_service_url)


def test_post_users():
    """ Adds two new users and checking that can't be two users with the same login"""

    first_user = {
        "login": "first_user",
        "password": "first_user_password",
        "first_name": "Oliver",
        "second_name": "Smith"
    }
    resp = requests.post(task_service_url + '/user', json=first_user)
    assert resp.status_code == 201

    second_user = {
        "login": "second_user",
        "password": "second_user_password",
        "first_name": "Liam",
        "second_name": "Williams"
    }
    resp = requests.post(task_service_url + '/user', json=second_user)
    assert resp.status_code == 201
    resp = requests.post(task_service_url + '/user', json=second_user)
    assert resp.status_code == 409


def user_authentication(user_id: int):
    """ Gets user session by user's id"""

    user_data = {1: {"login": "first_user",
                     "password": "first_user_password"},
                 2: {
                     "login": "second_user",
                     "password": "second_user_password"}}
    resp = requests.post(task_service_url + '/user/authentication', json=user_data[user_id])
    assert resp.status_code == 200
    return {"accept": "application/json",
            "token": resp.json()["access_token"],
            "Content-Type": "application/json"}


def test_post_task():
    """ Adds three task for first user and another three for second user"""

    task_data = {
        "title": "some_title",
        "content": "some_content"
    }
    # First user posts three task with ids 1, 2, 3
    for _ in range(3):
        resp = requests.post(task_service_url + '/task', json=task_data, headers=user_authentication(1))
        assert resp.status_code == 201

    # Second user posts three task with ids 4, 5, 6
    for _ in range(3):
        resp = requests.post(task_service_url + '/task', json=task_data, headers=user_authentication(2))
        assert resp.status_code == 201


def test_giving_permission():
    """ Tests that before giving permission task is forbidden, """
    """only creator can give permission and after giving rights resource is available"""

    # Before giving rights
    resp = requests.get(task_service_url + '/task/2', headers=user_authentication(2))
    assert resp.status_code == 403

    permission_data = {
        "access_user_login": "second_user",
        "task_id": 2,
        "access_mode": 2  # 2 = changing rights
    }
    # Only creator can provide permission

    resp = requests.post(task_service_url + '/permission', json=permission_data, headers=user_authentication(2))
    assert resp.status_code == 403

    # First user provides changing right to second user on task with id = 2

    resp = requests.post(task_service_url + '/permission', json=permission_data, headers=user_authentication(1))
    assert resp.status_code == 201

    # After giving rights
    resp = requests.put(task_service_url + '/task', json={
        "task_id": 2,
        "new_title": "changing title",
        "new_content": "changing content"
    }, headers=user_authentication(2))
    assert resp.status_code == 200


def test_deleting_task():
    """ Tests that only creator can delete task"""

    # Second user can't delete task even with changing rights
    resp = requests.delete(task_service_url + '/task/2', headers=user_authentication(2))
    assert resp.status_code == 403

    # First user deletes task 2 ( First user is owner)
    resp = requests.delete(task_service_url + '/task/2', headers=user_authentication(1))
    assert resp.status_code == 204

    # Content now doesn't exist

    resp = requests.get(task_service_url + '/task/2', headers=user_authentication(1))
    assert resp.status_code == 404


def test_rights_deleting():
    """ Tests that after deleting task permissions on that task doesn't exist """
    """and that user can't delete rights that was not given"""

    # Permission that was given to second user does not exist after deleting task
    resp = requests.delete(task_service_url + '/permission/second_user/2', headers=user_authentication(1))

    assert resp.status_code == 404

    # Can't delete rights that was not given
    resp = requests.delete(task_service_url + '/permission/second_user/1', headers=user_authentication(1))
    assert resp.status_code == 404
