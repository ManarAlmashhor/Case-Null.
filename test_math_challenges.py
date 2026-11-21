from copy import deepcopy
import json

import pytest

from backend.math_challenges import challenge_catalog, grade_challenge, progress_status
from backend.main import ConclusionRequest, submit_conclusion


RECORDS = ["access-register", "authentication-log", "workstation-record", "location-verification"]
ANSWERS = {
    "logic": {"rule": "all", "truth": ["0", "1", "0", "0", "1"], "contradiction": "no"},
    "structures": {"c1": ["A", "S", "K"], "c2": ["S", "K"], "c3": ["S", "K"], "function": "yes", "injective": "no"},
    "induction": {"base": "U", "hypothesis": "all", "step": "intersection", "reason": "and", "unchanged": ["S", "K"]},
    "counting": {"subsets": "64", "bundles": "20", "pairs": "10"},
    "relations": {"matrix": ["1", "0", "1", "1", "0", "0", "0", "0", "1", "1"], "composition": ["S", "K"], "final": ["K"], "scope": "compatible"},
}


def complete_work():
    work = []
    for challenge_id, answers in ANSWERS.items():
        response = grade_challenge(challenge_id, answers, work, RECORDS)
        assert response["correct"]
        work = response["work"]
    return work


def test_five_chapters_solve_real_case_and_survive_json_round_trip():
    work = json.loads(json.dumps(complete_work()))
    status = progress_status(work, RECORDS)
    assert status["work"] == work
    assert status["completed"] == list(ANSWERS)
    response = grade_challenge("relations", ANSWERS["relations"], work, RECORDS)
    assert response["deduction"]["accounts"] == ["K"]
    assert set(response["deduction"]["documents"]) == set(RECORDS)


def test_catalog_and_wrong_attempt_do_not_return_solution_keys():
    catalog = challenge_catalog()
    assert len(catalog["challenges"]) == 5
    assert all("solution" not in item and "answers" not in item for item in catalog["challenges"])
    wrong = {**ANSWERS["logic"], "truth": ["1"] * 5}
    result = grade_challenge("logic", wrong, [], RECORDS)
    assert not result["correct"]
    assert "solution" not in result and "deduction" not in result and "work" not in result
    assert result["checks"] == [{"key": "rule", "correct": True}, {"key": "truth", "correct": False}, {"key": "contradiction", "correct": True}]


def test_chapter_skipping_and_missing_sources_are_blocked():
    assert grade_challenge("relations", ANSWERS["relations"], [], RECORDS)["blocked"]
    assert grade_challenge("logic", ANSWERS["logic"], [], ["access-register"])["blocked"]
    work = complete_work()[:4]
    assert grade_challenge("relations", ANSWERS["relations"], work, RECORDS[:3])["blocked"]


def test_modified_saved_answers_invalidate_dependent_chapters():
    work = deepcopy(complete_work())
    work[1]["answers"]["c1"] = ["K"]
    status = progress_status(work, RECORDS)
    assert status["completed"] == ["logic"]
    assert "relations" not in status["reviews"]


def test_rechecking_completed_chapter_preserves_later_work():
    work = complete_work()
    result = grade_challenge("logic", ANSWERS["logic"], work, RECORDS)
    assert result["work"] == work


@pytest.mark.parametrize("bad_value", [[], ["S", "K", "K"], ["S", {"id": "K"}], "S,K", None])
def test_invalid_or_duplicate_set_members_cannot_pass(bad_value):
    work = complete_work()[:1]
    answer = {**ANSWERS["structures"], "c2": bad_value}
    assert not grade_challenge("structures", answer, work, RECORDS)["correct"]


def test_counting_accepts_integer_answers_and_rejects_booleans():
    work = complete_work()[:3]
    assert grade_challenge("counting", {"subsets": 64, "bundles": 20, "pairs": 10}, work, RECORDS)["correct"]
    assert not grade_challenge("counting", {"subsets": True, "bundles": 20, "pairs": 10}, work, RECORDS)["correct"]


def test_final_report_requires_revalidated_mathematics_even_for_right_account():
    draft = dict(candidate="K", documents=RECORDS, reasoning="Permission, time and workstation records plus the verified alibi support this account under the direct-use assumption.")
    assert not submit_conclusion(ConclusionRequest(**draft))["accepted"]
    work = complete_work()
    assert submit_conclusion(ConclusionRequest(**draft, math_work=work))["accepted"]
    work[3]["answers"]["bundles"] = "19"
    assert not submit_conclusion(ConclusionRequest(**draft, math_work=work))["accepted"]
