"""Appendix A, unchanged, plus explicitly separate synthetic evaluation cases."""
from copy import deepcopy
from .engine import public_case

SOURCE_DATA = {
    'E1': ('access-register', 'Research-file permission register', None, 'Record capture time not specified'),
    'E2': ('authentication-log', 'Verified authentication log', '10:00–10:30 PM', 'Incident login window'),
    'E3': ('workstation-record', 'Lab-PC2 activity record', None, 'Individual event timestamps not specified'),
    'E4': ('location-verification', 'Validated physical-location record', None, 'Alibi verification timestamp not specified'),
    'E5': ('account-directory', 'Synthetic account directory', None, 'Directory capture time not specified'),
    'E6': ('training-register', 'Laboratory access-training register', None, 'Training completion dates not specified'),
}
BENCHMARKS = {
    'BENCH-EMPTY': {'name': 'Disjoint access and login conditions', 'sets': [['A'], ['S', 'O'], ['S', 'K'], ['A', 'O', 'L', 'K'], ['A', 'S', 'O', 'L', 'K'], ['A', 'S', 'L', 'K']]},
    'BENCH-MULTIPLE': {'name': 'Multiple compatible accounts', 'sets': [['A', 'S', 'K'], ['S', 'K'], ['S', 'K'], ['A', 'S', 'O', 'L', 'K'], ['A', 'S', 'O', 'L', 'K'], ['A', 'S', 'L', 'K']]},
    'BENCH-UNKNOWN': {'name': 'Unverified training information', 'unknown': 'E6'},
    'BENCH-CONFLICT': {'name': 'Incompatible mandatory statements', 'conflicting': True},
    'BENCH-DISPUTED': {'name': 'Disputed provisional training record', 'disputed': 'E6', 'sets': [['A', 'S', 'K'], ['S', 'O', 'K'], ['S', 'K'], ['A', 'O', 'L', 'K'], ['A', 'S', 'O', 'L', 'K'], ['O']]},
}


def get_case(case_id='CASE-001'):
    if case_id != 'CASE-001' and case_id not in BENCHMARKS:
        raise ValueError('Unknown case identifier')
    case = deepcopy(public_case())
    fixture = BENCHMARKS.get(case_id, {})
    case.update({'id': case_id, 'name': fixture.get('name', case['name']), 'research_example': case_id == 'CASE-001', 'default_conflicting': fixture.get('conflicting', False), 'scope': 'Direct physical use of Lab-PC2 is the investigated hypothesis. Remote access is outside this scenario.', 'source_note': 'Research Appendix A: exact illustrative case.' if case_id == 'CASE-001' else 'Additional manually specified synthetic benchmark; not an alteration of Appendix A.'})
    for index, clue in enumerate(case['clues']):
        source_id, source, time, time_note = SOURCE_DATA[clue['id']]
        clue.update({'source_id': source_id, 'source': source, 'time': time, 'time_note': time_note, 'reliability': 'VERIFIED', 'mandatory': True, 'truth_status': 'VERIFIED_SYNTHETIC_BOOLEAN'})
        if 'sets' in fixture:
            clue['matches'] = fixture['sets'][index]
        if fixture.get('unknown') == clue['id']:
            clue.update({'matches': [], 'reliability': 'UNKNOWN', 'mandatory': False, 'truth_status': 'UNKNOWN'})
        if fixture.get('disputed') == clue['id']:
            clue.update({'reliability': 'DISPUTED', 'mandatory': False, 'truth_status': 'PROVISIONAL'})
    if fixture:
        for person in case['suspects']:
            for clue in case['clues']:
                person[clue['field']] = None if clue['reliability'] == 'UNKNOWN' else int(person['id'] in clue['matches'])
            # These are declared fixture values, never substituted into Appendix A.
            person['last_login'] = '10:12 PM' if person['T'] else ('No verified event' if person['id'] == 'L' else '5:00 PM')
    return case


def case_catalog():
    return [{'id': case_id, 'name': get_case(case_id)['name'], 'research_example': case_id == 'CASE-001'} for case_id in ['CASE-001', *BENCHMARKS]]
