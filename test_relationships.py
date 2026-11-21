from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def verify(account, doc, discovered=None):
    response = client.post('/api/discovery/relationships/verify', json={
        'account': account, 'document_id': doc,
        'discovered': discovered if discovered is not None else [doc]})
    assert response.status_code == 200
    return response.json()

def test_real_access_relations():
    assert verify('A','access-register')['status'] == 'supported'
    assert verify('O','access-register')['status'] == 'unsupported'
    assert verify('S','access-register')['relation'] == 'R_access'

def test_workstation_relation():
    assert verify('K','workstation-record')['status'] == 'supported'
    assert verify('L','workstation-record')['status'] == 'unsupported'

def test_alibi_is_not_assumed_from_missing_data():
    assert verify('S','location-verification')['status'] == 'supported'
    assert verify('K','location-verification')['status'] == 'unknown'

def test_no_undiscovered_links():
    response = client.post('/api/discovery/relationships/verify', json={
        'account':'S', 'document_id':'access-register', 'discovered':[]})
    assert response.status_code == 422

def test_no_guilt_is_returned_by_link_check():
    result = verify('S','authentication-log')
    assert 'candidates' not in result and 'guilty' not in str(result).lower()
