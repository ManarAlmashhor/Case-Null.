"""Independent, manually specified Boolean baselines and exhaustive evaluation.

Bit positions E1..E6 encode the manually reviewed condition table, not output
from the filtering engine. Unknown/disputed columns are explicitly ignored.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from .research import analyze_research

BASELINES = {
    'CASE-001': {'bits': {'A': 57, 'S': 55, 'O': 26, 'L': 56, 'K': 63}, 'ignored_mask': 0, 'not_p': False},
    'BENCH-EMPTY': {'bits': {'A': 57, 'S': 54, 'O': 26, 'L': 56, 'K': 60}, 'ignored_mask': 0, 'not_p': False},
    'BENCH-MULTIPLE': {'bits': {'A': 57, 'S': 63, 'O': 24, 'L': 56, 'K': 63}, 'ignored_mask': 0, 'not_p': False},
    'BENCH-UNKNOWN': {'bits': {'A': 25, 'S': 23, 'O': 26, 'L': 24, 'K': 31}, 'ignored_mask': 32, 'not_p': False},
    'BENCH-CONFLICT': {'bits': {'A': 57, 'S': 55, 'O': 26, 'L': 56, 'K': 63}, 'ignored_mask': 0, 'not_p': True},
    'BENCH-DISPUTED': {'bits': {'A': 25, 'S': 23, 'O': 58, 'L': 24, 'K': 31}, 'ignored_mask': 32, 'not_p': False},
}
EVALUATION_DIR = Path(__file__).resolve().parent.parent / 'evaluation'


def expected_candidates(case_id, mask):
    baseline = BASELINES[case_id]
    required = mask & ~baseline['ignored_mask']
    if baseline['not_p'] and required & 1:
        return None
    return [sid for sid, bits in baseline['bits'].items() if bits & required == required and not (baseline['not_p'] and bits & 1)]


def run_evaluation(save=False):
    started = perf_counter()
    checks, cases = [], []
    for case_id in BASELINES:
        case_checks = []
        for mask in range(64):
            selected = [f'E{index + 1}' for index in range(6) if mask & (1 << index)]
            expected = expected_candidates(case_id, mask)
            actual = analyze_research(selected=selected, case_id=case_id)
            correct = actual['candidates'] == expected
            traceable = all(exclusion['clue'] in [*actual['applied_clues'], *(['X1'] if actual['conflicting_test'] else [])] and exclusion.get('source') and exclusion.get('rule') for exclusion in actual['exclusions'])
            resolved_safely = not actual['contradiction'] or (actual['candidates'] is None and all(item['status'] == 'UNRESOLVED' for item in actual['decisions']))
            ignored_safely = all(not item['applied'] for item in actual['selected_evidence'] if item['reliability'] != 'VERIFIED' or not item['mandatory'])
            row = {'case_id': case_id, 'mask': mask, 'selected': selected, 'expected': expected, 'actual': actual['candidates'], 'status': actual['status'], 'candidate_set_correct': correct, 'exclusions_traceable': bool(traceable), 'contradiction_safe': resolved_safely, 'unknown_disputed_safe': ignored_safely, 'passed': bool(correct and traceable and resolved_safely and ignored_safely)}
            checks.append(row); case_checks.append(row)
        cases.append({'case_id': case_id, 'patterns': 64, 'passed': sum(row['passed'] for row in case_checks), 'statuses': sorted({row['status'] for row in case_checks})})
    report = {'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'evaluation_type': 'Automated deterministic correctness and traceability checks', 'baseline_method': 'Manually specified six-column Boolean tables encoded as independent bitmasks. No baseline is inferred from the engine output.', 'case_count': len(cases), 'pattern_count': len(checks), 'passed': sum(row['passed'] for row in checks), 'failed': sum(not row['passed'] for row in checks), 'duration_seconds': round(perf_counter() - started, 4), 'candidate_set_matches': sum(row['candidate_set_correct'] for row in checks), 'traceability_passes': sum(row['exclusions_traceable'] for row in checks), 'cases': cases, 'checks': checks, 'human_study': {'status': 'NOT_CONDUCTED', 'participants': None, 'comprehension_results': None, 'usability_results': None, 'note': 'Automated tests do not establish usability, learning gains, forensic validity, or novelty. Participant tasks, consent safeguards and an objective rubric are supplied separately.'}}
    if save:
        EVALUATION_DIR.mkdir(exist_ok=True)
        (EVALUATION_DIR / 'automated-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        (EVALUATION_DIR / 'manual-baselines.json').write_text(json.dumps(BASELINES, indent=2), encoding='utf-8')
        with (EVALUATION_DIR / 'automated-results.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(checks[0]))
            writer.writeheader(); writer.writerows(checks)
    return report


def latest_evaluation():
    path = EVALUATION_DIR / 'automated-results.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'status': 'NOT_RUN', 'human_study': {'status': 'NOT_CONDUCTED'}}


if __name__ == '__main__':
    result = run_evaluation(save=True)
    print(f'{result["passed"]}/{result["pattern_count"]} patterns passed across {result["case_count"]} synthetic cases; {result["failed"]} failed. Human study: NOT CONDUCTED.')
    raise SystemExit(1 if result['failed'] else 0)
