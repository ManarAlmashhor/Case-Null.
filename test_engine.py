from itertools import combinations
from backend.engine import analyze,public_case,CLUE_IDS

def test_initial():
    assert analyze()['candidates']==['A','S','O','L','K']
def test_research_example():
    assert analyze(['E1','E2','E3'])['candidates']==['S','K']
    assert analyze(['E1','E2','E3','E4'])['candidates']==['K']
def test_all_64_combinations():
    for n in range(7):
        for selection in combinations(CLUE_IDS,n):
            result=analyze(list(selection))
            expected=[s['id'] for s in public_case()['suspects'] if all(s[c['field']]==1 for c in public_case()['clues'] if c['id'] in selection)]
            assert result['candidates']==expected
            assert result['trace'][-1]['candidates']==expected

def test_sympy_contradiction():
    assert analyze(['E1'],conflicting=True)['contradiction'] is True
    assert analyze(['E1'],conflicting=True)['candidates'] is None
    assert analyze(['E2'],conflicting=True)['contradiction'] is False

def test_unknown_does_not_exclude():
    assert analyze(['E1'],unknown=True)['candidates']==analyze(['E1'])['candidates']

def test_counting():
    assert analyze()['counting']=={'all_selection_patterns':64,'choose_three_clues':20,'two_suspect_pairs':10}
