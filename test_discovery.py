import pytest
from backend.discovery import discovery_case, source_document, check_conclusion, CORE_DOCUMENTS
from backend.engine import SUSPECTS, analyze

REASONING = "My conclusion follows from the combined access, authentication, device and physical-location records cited in this submission."


def test_discovery_catalog_does_not_supply_the_deduction():
    case = discovery_case()
    assert len(case['suspects']) == 5
    assert len(case['documents']) == 6
    assert all(set(person) == {'id', 'name', 'role'} for person in case['suspects'])
    assert all(set(document) == {'id', 'title', 'folder'} for document in case['documents'])
    assert 'candidates' not in case and 'clues' not in case


def test_source_records_preserve_missing_information_and_research_data():
    records = source_document('authentication-log')
    assert records['rows'][3]['values'][-1] == 'No verified event'
    permission_rows = source_document('access-register')['rows']
    assert [row['account'] for row in permission_rows if row['values'][2] == 'Allowed'] == ['A', 'S', 'K']
    assert 'clue' not in records and 'candidates' not in records and 'matches' not in records


def test_incomplete_submission_does_not_reveal_the_answer():
    candidate = analyze(['E1', 'E2', 'E3', 'E4'])['candidates'][0]
    result = check_conclusion(candidate, ['access-register'], REASONING)
    assert result['accepted'] is False
    assert set(result) == {'accepted', 'message', 'status'}
    assert result['status'] == 'insufficient'
    assert not any(person['name'] in result['message'] for person in SUSPECTS.values())


def test_wrong_submissions_do_not_leak_the_expected_account():
    expected = analyze(['E1', 'E2', 'E3', 'E4'])['candidates'][0]
    for candidate in SUSPECTS:
        if candidate != expected:
            result = check_conclusion(candidate, list(CORE_DOCUMENTS), REASONING)
            assert result['accepted'] is False
            assert 'review' not in result
            assert not any(person['name'] in result['message'] for person in SUSPECTS.values())


def test_supported_conclusion_unlocks_mathematical_review():
    expected = analyze(['E1', 'E2', 'E3', 'E4'])['candidates'][0]
    result = check_conclusion(expected, list(CORE_DOCUMENTS), REASONING)
    assert result['accepted'] is True
    assert result['review']['candidates'] == [expected]


def test_blank_reasoning_does_not_unlock_review():
    expected = analyze(['E1', 'E2', 'E3', 'E4'])['candidates'][0]
    assert check_conclusion(expected, list(CORE_DOCUMENTS), '')['accepted'] is False


def test_unknown_or_duplicate_source_ids_are_rejected():
    with pytest.raises(ValueError):
        source_document('invented-record')
    with pytest.raises(ValueError):
        check_conclusion('A', ['invented-record'], REASONING)
    with pytest.raises(ValueError):
        check_conclusion('A', ['access-register', 'access-register'], REASONING)
