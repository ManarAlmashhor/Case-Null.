"""Executable research requirements: auditable filtering and all five chapters."""
from itertools import combinations
from math import comb
from sympy import And, Not, Symbol, satisfiable
from .cases import get_case
from .engine import ACCESS_RELATION, DEVICE_RELATION


def analyze_research(selected=None, conflicting=None, unknown=False, provisional=None, case_id='CASE-001'):
    case = get_case(case_id)
    selected = selected or []
    provisional = provisional or []
    clues = {clue['id']: clue for clue in case['clues']}
    for values in (selected, provisional):
        if len(values) != len(set(values)) or any(value not in clues for value in values):
            raise ValueError('Clue identifiers must be unique valid identifiers for this case')
    selected = [cid for cid in clues if cid in selected]
    if conflicting is None:
        conflicting = case['default_conflicting']
    people = case['suspects']
    order = [person['id'] for person in people]
    ordered = lambda values: [sid for sid in order if sid in values]
    formatted = lambda values: '{' + ', '.join(ordered(values)) + '}'
    remaining = set(order)
    trace = [{'clue': 'C0', 'label': 'All fictional identities', 'operation': f'C₀ = U = {formatted(remaining)}', 'before': order, 'evidence_set': order, 'candidates': order, 'removed': [], 'applied': True, 'rule': 'Base case: no selected conditions.'}]
    exclusions, applied, ignored = [], [], []
    selected_evidence = []
    for cid in selected:
        clue = {**clues[cid], 'mandatory': clues[cid]['mandatory'] and cid not in provisional}
        usable = clue['reliability'] == 'VERIFIED' and clue['mandatory']
        selected_evidence.append({**clue, 'applied': usable})
        previous = remaining.copy()
        if not usable:
            reason = 'Provisional or disputed evidence is not a mandatory exclusion condition.' if clue['reliability'] != 'UNKNOWN' else 'Truth value UNKNOWN is not treated as false.'
            ignored.append({'clue': cid, 'reason': reason})
            trace.append({'clue': cid, 'label': clue['label'], 'operation': f'{cid} not applied; C = {formatted(remaining)}', 'before': ordered(previous), 'evidence_set': None if clue['reliability'] == 'UNKNOWN' else clue['matches'], 'candidates': ordered(remaining), 'removed': [], 'applied': False, 'rule': reason, 'source': clue['source']})
            continue
        applied.append(cid)
        matched = set(clue['matches'])
        remaining &= matched
        for sid in ordered(previous - remaining):
            exclusions.append({'suspect': sid, 'clue': cid, 'reason': f'Does not satisfy: {clue["description"]}', 'rule': 'Cₖ = Cₖ₋₁ ∩ Eₖ', 'source': clue['source']})
        index = len(applied)
        trace.append({'clue': cid, 'label': clue['label'], 'operation': f'C{index} = {formatted(previous)} ∩ {formatted(matched)} = {formatted(remaining)}', 'before': ordered(previous), 'evidence_set': ordered(matched), 'candidates': ordered(remaining), 'removed': ordered(previous - remaining), 'applied': True, 'rule': 'Retain exactly those satisfying every selected verified mandatory condition.', 'source': clue['source']})
    P = Symbol('P')
    constraints = ([P] if 'E1' in applied else []) + ([Not(P)] if conflicting else [])
    contradiction = bool(constraints) and satisfiable(And(*constraints)) is False
    conflict_record = None
    if conflicting:
        conflict_record = {'id': 'X1', 'label': 'Injected verified NOT P condition', 'source': 'Explicit consistency-test input, separate from the research records', 'time': None, 'time_note': 'No evidence timestamp specified for this test', 'reliability': 'VERIFIED', 'mandatory': True, 'formula': '¬P', 'truth_status': 'TEST_CONSTRAINT'}
        if contradiction:
            trace.append({'clue': 'X1', 'label': conflict_record['label'], 'operation': 'P ∧ ¬P is UNSATISFIABLE; conclusion suspended.', 'candidates': None, 'removed': [], 'applied': True, 'rule': 'SymPy satisfiability check; contradictory mandatory statements cannot support a conclusion.', 'source': conflict_record['source']})
        else:
            previous = remaining.copy()
            not_p = {person['id'] for person in people if person['P'] == 0}
            remaining &= not_p
            for sid in ordered(previous - remaining):
                exclusions.append({'suspect': sid, 'clue': 'X1', 'reason': 'The injected verified test requires NOT P.', 'rule': 'C ← C ∩ ¬P', 'source': conflict_record['source']})
            trace.append({'clue': 'X1', 'label': conflict_record['label'], 'operation': f'C = {formatted(previous)} ∩ {formatted(not_p)} = {formatted(remaining)}', 'before': ordered(previous), 'evidence_set': ordered(not_p), 'candidates': ordered(remaining), 'removed': ordered(previous - remaining), 'applied': True, 'rule': 'Apply the non-contradictory verified NOT P test.', 'source': conflict_record['source']})
    unknown_record = {'id': 'U1', 'description': 'Unverified possible remote login. Visible for discussion; remote access remains outside the case hypothesis.', 'source': 'Explicit unknown-data test input', 'time': None, 'time_note': 'Unknown; no timestamp invented', 'reliability': 'UNKNOWN', 'mandatory': False, 'truth_status': 'UNKNOWN', 'applied': False} if unknown else None
    rows = []
    for person in people:
        eligible = int(all(person[field] == 1 for field in ('P', 'T', 'W')))
        physical = int(bool(eligible) and person['N'] == 1)
        rows.append({'id': person['id'], 'name': person['name'], **{field: person[field] for field in ('P', 'T', 'W', 'N', 'active', 'training')}, 'eligible_result': eligible, 'physical_result': physical, 'and_result': physical, 'selected_result': None if contradiction else int(person['id'] in remaining)})
    eligible_ids = [row['id'] for row in rows if row['eligible_result']]
    physical_ids = [row['id'] for row in rows if row['physical_result']]
    decisions = []
    for person in people:
        failures = [{'clue': cid, 'condition': clues[cid]['description'], 'source': clues[cid]['source'], 'rule': 'A required predicate is false for this identity.'} for cid in applied if person['id'] not in clues[cid]['matches']]
        if conflicting and person['P'] == 1:
            failures.append({'clue': 'X1', 'condition': 'Injected NOT P test', 'source': conflict_record['source'], 'rule': 'The test requires ¬P.'})
        status = 'UNRESOLVED' if contradiction else ('INCLUDED' if person['id'] in remaining else 'EXCLUDED')
        reason = 'Conclusion suspended because mandatory premises contradict.' if contradiction else ('Satisfies every selected verified mandatory condition.' if applied or conflicting else 'No mandatory conditions selected; retained by the base case.') if status == 'INCLUDED' else 'Fails one or more selected verified mandatory conditions.'
        decisions.append({'id': person['id'], 'name': person['name'], 'status': status, 'reason': reason, 'failed_conditions': failures, 'satisfied_clues': [cid for cid in applied if person['id'] in clues[cid]['matches']], 'satisfied_conditions': [{'clue': cid, 'condition': clues[cid]['description'], 'source': clues[cid]['source'], 'rule': 'The required predicate is true for this identity.'} for cid in applied if person['id'] in clues[cid]['matches']]})
    # Core relations are exact in CASE-001. Additional cases derive their declared fixtures.
    access = list(ACCESS_RELATION) if case_id == 'CASE-001' else [(person['id'], 'research.pdf') for person in people if person['P'] == 1] + [('S', 'draft.txt'), ('O', 'draft.txt')]
    devices = list(DEVICE_RELATION) if case_id == 'CASE-001' else [(person['id'], 'Lab-PC2') for person in people if person['W'] == 1]
    access_matrix = [{'id': person['id'], 'name': person['name'], **{file: int((person['id'], file) in access) for file in case['files']}} for person in people]
    device_matrix = [{'id': person['id'], 'name': person['name'], **{device: int((person['id'], device) in devices) for device in case['devices']}} for person in people]
    status = 'CONTRADICTION' if contradiction else 'NO_MATCH' if not remaining else 'ONE_CANDIDATE' if len(remaining) == 1 else 'MULTIPLE_CANDIDATES'
    result = {
        'case_id': case_id, 'case_name': case['name'], 'status': status, 'selected': selected, 'applied_clues': applied, 'ignored_clues': ignored, 'selected_evidence': selected_evidence,
        'candidates': None if contradiction else ordered(remaining), 'contradiction': contradiction, 'conflicting_test': conflicting, 'conflict_record': conflict_record,
        'warning': 'Contradictory verified mandatory conditions: P and NOT P. Conclusion suspended.' if contradiction else 'No identity satisfies all selected verified mandatory conditions. Check the premises; do not invent a new culprit.' if not remaining else None,
        'unknown_record': unknown_record, 'trace': trace, 'exclusions': exclusions, 'decisions': decisions,
        'logic': {'eligible': 'Eligible(x) = P(x) ∧ T(x) ∧ W(x)', 'physical': 'PhysicalCandidate(x) = P(x) ∧ T(x) ∧ W(x) ∧ N(x)', 'selected': ' ∧ '.join([clues[cid]['field'] + '(x)' for cid in applied] + (['¬P(x)'] if conflicting else [])) or 'TRUE (empty conjunction)', 'eligible_candidates': eligible_ids, 'physical_candidates': physical_ids, 'implication': 'Eligible(x) ⇒ P(x)', 'implication_valid': satisfiable(And(Symbol('P'), Symbol('T'), Symbol('W'), Not(Symbol('P')))) is False, 'proof': 'Conjunction elimination: if P ∧ T ∧ W holds, P holds. SymPy confirms the negation of this implication has no model.', 'quantifiers': {'exists_eligible': bool(eligible_ids), 'all_eligible': len(eligible_ids) == len(people), 'exists_physical': bool(physical_ids), 'all_physical': len(physical_ids) == len(people)}},
        'matrix': rows,
        'sets': {'universe': order, 'clue_sets': {cid: None if clue['reliability'] == 'UNKNOWN' else clue['matches'] for cid, clue in clues.items()}, 'candidate_formula': 'C₀ = U; Cₖ = Cₖ₋₁ ∩ Eₖ', 'equivalent_formula': 'Cₖ = U ∩ E₁ ∩ E₂ ∩ … ∩ Eₖ'},
        'functions': {'role_domain': 'U', 'role_codomain': 'Roles', 'role': {person['id']: person['role'] for person in people}, 'last_login_domain': 'U', 'last_login_codomain': 'Time ∪ {No verified event}', 'last_login': {person['id']: person['last_login'] or 'No verified event' for person in people}},
        'induction': {'base': 'k = 0: C₀ = U, so every identity satisfies the empty collection of conditions.', 'hypothesis': 'After k processed mandatory clues, Cₖ contains exactly the identities satisfying all k verified conditions.', 'step': 'Cₖ₊₁ = Cₖ ∩ Eₖ₊₁ = U ∩ E₁ ∩ … ∩ Eₖ ∩ Eₖ₊₁. Thus the invariant holds for k+1.', 'conclusion': 'By induction, filtering is correct for any finite number of selected verified mandatory clues.', 'processed': len(applied), 'limitation': 'The proof establishes correctness relative to the encoded clues, not the truth of the clues themselves.'},
        'counting': {'all_selection_patterns': 2 ** len(clues), 'choose_three_clues': comb(len(clues), 3), 'two_suspect_pairs': comb(len(people), 2), 'formulas': ['2⁶ = 64', 'C(6,3) = 6! / (3!3!) = 20', 'C(5,2) = 5! / (2!3!) = 10'], 'three_clue_combinations': [list(values) for values in combinations(clues, 3)], 'suspect_pairs': [list(values) for values in combinations(order, 2)], 'interpretation': 'Counts describe possible configurations, not guilt or probabilistic confidence.'},
        'relations': {'users': order, 'files': case['files'], 'devices': case['devices'], 'file_access': [list(pair) for pair in access], 'device_activity': [list(pair) for pair in devices], 'access_matrix': access_matrix, 'device_matrix': device_matrix, 'inverse_research_file': ordered({sid for sid, file in access if file == 'research.pdf'}), 'cross_set_note': 'These relations connect different sets. Reflexive and symmetric tests for a relation on one set must not be applied indiscriminately.'},
        'activity_log': [{'event': index, 'clue': step['clue'], 'operation': step['operation'], 'source': step.get('source', 'Synthetic case repository')} for index, step in enumerate(trace)],
        'case_limit': 'Fictional classroom simulation. The investigated hypothesis is direct physical use of Lab-PC2; remote access is excluded. Account activity does not prove who operated the workstation. Logically possible candidates are not proven guilty.',
    }
    result['report_text'] = report_text(case, result)
    return result


def report_text(case, result):
    lines = ['CASE: NULL — INVESTIGATION REPORT', f'Case: {case["id"]} / {case["name"]}', case['source_note'], f'Status: {result["status"]}', 'Result: ' + ('UNRESOLVED' if result['candidates'] is None else '{' + ', '.join(result['candidates']) + '}'), '', 'SELECTED EVIDENCE AND SOURCES']
    for clue in result['selected_evidence']:
        lines.append(f'{clue["id"]}: {clue["label"]} | {clue["source"]} | Time: {clue["time"] or "Not specified"} | {clue["reliability"]} | Mandatory: {clue["mandatory"]} | Applied: {clue["applied"]}')
    for record in (result['conflict_record'], result['unknown_record']):
        if record: lines.append(f'{record["id"]}: {record["source"]} | {record["reliability"]} | Mandatory: {record["mandatory"]} | Time not specified')
    lines += ['', 'SET OPERATIONS AND APPLICABLE RULES']
    lines += [step['operation'] + ' — ' + step['rule'] for step in result['trace']]
    lines += ['', 'INCLUSION AND EXCLUSION EXPLANATIONS']
    for decision in result['decisions']:
        lines.append(f'{decision["name"]} ({decision["id"]}): {decision["status"]}. {decision["reason"]}')
        lines += [f'  {failure["clue"]}: {failure["condition"]}; source: {failure["source"]}; rule: {failure["rule"]}' for failure in decision['failed_conditions']]
        if decision['status'] == 'INCLUDED':
            lines += [f'  Satisfied {item["clue"]}: {item["condition"]}; source: {item["source"]}; rule: {item["rule"]}' for item in decision['satisfied_conditions']]
    lines += ['', 'LOGIC', result['logic']['eligible'], result['logic']['physical'], result['logic']['selected'], result['logic']['implication'], result['logic']['proof'], str(result['logic']['quantifiers']), '', 'INDUCTION', result['induction']['base'], result['induction']['hypothesis'], result['induction']['step'], result['induction']['limitation'], '', 'COUNTING', *result['counting']['formulas'], result['counting']['interpretation'], '', 'RELATION LINKS', 'Raccess = ' + str(result['relations']['file_access']), 'Rdevice = ' + str(result['relations']['device_activity']), 'Raccess inverse(research.pdf) = ' + str(result['relations']['inverse_research_file']), result['relations']['cross_set_note'], '', 'CONSISTENCY AND LIMITATIONS', result['warning'] or 'No consistency warning.', result['case_limit']]
    return '\n'.join(lines)
