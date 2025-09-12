from http import HTTPStatus
import pytest


@pytest.fixture
def casal_token(client):
    resp = client.post(
        '/users/',
        json={
            'username': 'casaltest',
            'email': 'casaltest@example.com',
            'password': 'senha123',
            'role': 'CASAL',
        },
    )
    assert resp.status_code == HTTPStatus.CREATED
    token_resp = client.post(
        '/auth/token',
        data={'username': 'casaltest@example.com', 'password': 'senha123'},
    )
    assert token_resp.status_code == HTTPStatus.OK
    return token_resp.json()['access_token']


@pytest.fixture
def wedding_list(client, casal_token):
    list_resp = client.post(
        '/lists/',
        json={'title': 'Lista Casamento', 'message': 'Bem-vindos'},
        headers={'Authorization': f'Bearer {casal_token}'},
    )
    assert list_resp.status_code == HTTPStatus.CREATED
    wl = list_resp.json()
    item_resp = client.post(
        f"/lists/{wl['id']}/items",
        json={'name': 'Panela', 'description': 'Inox'},
        headers={'Authorization': f'Bearer {casal_token}'},
    )
    assert item_resp.status_code == HTTPStatus.CREATED
    wl['items'] = [item_resp.json()]
    return wl


@pytest.fixture
def guest_token(client):
    create = client.post(
        '/users/',
        json={
            'username': 'guestlogin',
            'email': 'guestlogin@example.com',
            'password': 'guestpass',
            'role': 'CONVIDADO',
        },
    )
    assert create.status_code == HTTPStatus.CREATED
    resp = client.post(
        '/auth/token',
        data={'username': 'guestlogin@example.com', 'password': 'guestpass'},
    )
    assert resp.status_code == HTTPStatus.OK
    return resp.json()['access_token']


@pytest.fixture
def list_with_item(client, casal_token):
    list_resp = client.post(
        '/lists/',
        json={'title': 'Lista 2'},
        headers={'Authorization': f'Bearer {casal_token}'},
    )
    wl = list_resp.json()
    item_resp = client.post(
        f"/lists/{wl['id']}/items",
        json={'name': 'Cafeteira'},
        headers={'Authorization': f'Bearer {casal_token}'},
    )
    return wl, item_resp.json()


def test_public_list_success(client, wedding_list, guest_token):
    response = client.get(
        f"/guest/lists/{wedding_list['shareable_link']}",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['title'] == 'Lista Casamento'
    assert len(body['items']) == 1


def test_public_list_not_found(client, guest_token):
    response = client.get('/guest/lists/naoexiste', headers={'Authorization': f'Bearer {guest_token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_reserve_item_success(client, guest_token, list_with_item):
    wl, item = list_with_item
    resp = client.post(
        f"/guest/items/{item['id']}/reserve",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    assert resp.status_code == HTTPStatus.CREATED
    body = resp.json()
    assert body['gift_item_id'] == item['id']


def test_reserve_item_conflict_if_not_available(client, guest_token, list_with_item):
    wl, item = list_with_item
    client.post(
        f"/guest/items/{item['id']}/reserve",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    resp2 = client.post(
        f"/guest/items/{item['id']}/reserve",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    assert resp2.status_code == HTTPStatus.CONFLICT


def test_cancel_reservation(client, guest_token, list_with_item):
    wl, item = list_with_item
    reserve_resp = client.post(
        f"/guest/items/{item['id']}/reserve",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    reservation_id = reserve_resp.json()['id']
    cancel_resp = client.delete(
        f"/guest/reservations/{reservation_id}",
        headers={'Authorization': f'Bearer {guest_token}'},
    )
    assert cancel_resp.status_code == HTTPStatus.OK


def test_rsvp_create_and_update(client, guest_token, list_with_item):
    wl, _ = list_with_item
    r1 = client.post(
        f"/guest/lists/{wl['id']}/rsvp",
        headers={'Authorization': f'Bearer {guest_token}'},
        params={'status': 'confirmed'},
    )
    assert r1.status_code == HTTPStatus.CREATED
    r2 = client.post(
        f"/guest/lists/{wl['id']}/rsvp",
        headers={'Authorization': f'Bearer {guest_token}'},
        params={'status': 'declined'},
    )
    assert r2.status_code == HTTPStatus.CREATED

