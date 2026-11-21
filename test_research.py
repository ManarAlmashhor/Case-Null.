import pytest
from backend.cases import get_case, case_catalog
from backend.research import analyze_research
from backend.benchmarks import run_evaluation


def test_exact_appendix_a_records_and_sets_are_preserved():
    case = get_case()
    assert [(p['id'], p['name'], p['role'], p['last_login']) for p in case['suspects']] == [('A','Ahmed','Administrator','5:35 PM'),('S','Sara','Researcher','10:14 PM'),('O','Omar','Student','10:09 PM'),('L','Lina','Student',None),('K','Khalid','Technician','10:21 PM')]
    assert [c['matches'] for c in case['clues']] == [['A','S','K'],['S','O','K'],['S','K'],['A','O','L','K'],['A','S','O','L','K'],['A','S','L','K']]
    assert case['incident_time'] == '10:25 PM' and case['computer'] == 'Lab-PC2' and case['file'] == 'research.pdf'


def test_literal_intersections_and_reversible_live_selections():
    result = analyze_research(['E4','E2','E1','E3'])
    assert result['selected'] == ['E1','E2','E3','E4']
    assert [row['candidates'] for row in result['trace']] == [['A','S','O','L','K'],['A','S','K'],['S','K'],['S','K'],['K']]
    assert result['trace'][1]['operation'] == 'C1 = {A, S, O, L, K} ∩ {A, S, K} = {A, S, K}'
    assert analyze_research(['E1','E2','E3'])['candidates'] == ['S','K']
    assert analyze_research([])['candidates'] == ['A','S','O','L','K']


def test_both_eligibility_rules_quantifiers_and_implication():
    result = analyze_research()
    assert result['logic']['eligible_candidates'] == ['S','K']
    assert result['logic']['physical_candidates'] == ['K']
    assert result['logic']['quantifiers'] == {'exists_eligible': True, 'all_eligible': False, 'exists_physical': True, 'all_physical': False}
    assert result['logic']['implication_valid'] is True
    sara = next(row for row in result['matrix'] if row['id'] == 'S')
    assert (sara['eligible_result'], sara['physical_result']) == (1, 0)
    assert result['functions']['last_login']['L'] == 'No verified event'


def test_source_metadata_does_not_invent_timestamps():
    for clue in get_case()['clues']:
        assert all(key in clue for key in ('source_id','source','time','time_note','reliability','mandatory','truth_status'))
        if clue['id'] != 'E2': assert clue['time'] is None


def test_unknown_disputed_and_provisional_are_not_false():
    assert analyze_research(['E6'], case_id='BENCH-UNKNOWN')['candidates'] == ['A','S','O','L','K']
    assert analyze_research(['E6'], case_id='BENCH-DISPUTED')['candidates'] == ['A','S','O','L','K']
    assert analyze_research(['E1'], provisional=['E1'])['candidates'] == ['A','S','O','L','K']
    baseline = analyze_research(['E1','E2'])
    unknown = analyze_research(['E1','E2'], unknown=True)
    assert unknown['candidates'] == baseline['candidates']
    assert unknown['unknown_record']['truth_status'] == 'UNKNOWN'
    assert unknown['unknown_record']['mandatory'] is False and unknown['unknown_record']['time'] is None


def test_unsatisfiability_is_distinct_from_an_empty_matching_set():
    contradiction = analyze_research(['E1'], conflicting=True)
    assert contradiction['status'] == 'CONTRADICTION' and contradiction['candidates'] is None
    assert all(decision['status'] == 'UNRESOLVED' for decision in contradiction['decisions'])
    empty = analyze_research(['E1','E2'], case_id='BENCH-EMPTY')
    assert empty['status'] == 'NO_MATCH' and empty['candidates'] == [] and not empty['contradiction']
    assert analyze_research(['E1'], provisional=['E1'], conflicting=True)['contradiction'] is False


def test_every_decision_is_explained_by_selected_verified_sources():
    result = analyze_research(['E1','E2','E3','E4'])
    assert len(result['decisions']) == 5
    for decision in result['decisions']:
        assert decision['reason']
        if decision['status'] == 'EXCLUDED':
            assert decision['failed_conditions']
            assert all(failure['clue'] in result['applied_clues'] and failure['source'] and failure['rule'] for failure in decision['failed_conditions'])


def test_exact_relations_inverse_and_both_incidence_matrices():
    relations = analyze_research()['relations']
    assert relations['file_access'] == [['A','research.pdf'],['S','research.pdf'],['K','research.pdf'],['S','draft.txt'],['O','draft.txt']]
    assert relations['device_activity'] == [['S','Lab-PC2'],['K','Lab-PC2']]
    assert relations['inverse_research_file'] == ['A','S','K']
    assert [row['draft.txt'] for row in relations['access_matrix']] == [0,1,1,0,0]
    assert all(row['Office-PC'] == 0 for row in relations['device_matrix'])


def test_counting_and_complete_report():
    result = analyze_research(['E1','E2','E3','E4'], unknown=True)
    assert (result['counting']['all_selection_patterns'],result['counting']['choose_three_clues'],result['counting']['two_suspect_pairs']) == (64,20,10)
    assert len(result['counting']['three_clue_combinations']) == 20 and len(result['counting']['suspect_pairs']) == 10
    for section in ('SELECTED EVIDENCE AND SOURCES','SET OPERATIONS','INCLUSION AND EXCLUSION','INDUCTION','COUNTING','RELATION LINKS','UNKNOWN'):
        assert section in result['report_text']
    assert 'Time: Not specified' in result['report_text']


def test_exhaustive_independent_benchmarks():
    report = run_evaluation()
    assert len(case_catalog()) == 6
    assert report['pattern_count'] == 384 and report['passed'] == 384 and report['failed'] == 0
    assert report['human_study']['status'] == 'NOT_CONDUCTED'
    assert report['human_study']['comprehension_results'] is None


def test_invalid_inputs_are_rejected():
    for values in (['E7'], ['E1','E1']):
        with pytest.raises(ValueError): analyze_research(values)
    with pytest.raises(ValueError): analyze_research([], case_id='NOT-A-CASE')
