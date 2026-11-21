"""Player-entered course exercises, checked against the synthetic case records.

Progress is a sequence of answers. Recompute every answer when resuming or
submitting a report so a saved completion flag cannot stand in for the work.
"""
from math import comb
import re

from .engine import SUSPECTS, CLUES, ACCESS_RELATION, DEVICE_RELATION, clue_set, sorted_codes
from .discovery import DOCUMENTS, CORE_DOCUMENTS

VERSION = "case-math-v1"
INITIAL_RECORDS = ["access-register", "authentication-log", "workstation-record"]


def choice(key, label, options):
    return {"key": key, "label": label, "type": "choice", "options": options}


def accounts(key, label):
    return {"key": key, "label": label, "type": "accounts"}


def number(key, label):
    return {"key": key, "label": label, "type": "number"}


def challenge_catalog():
    people = [{"id": code, "name": person["name"]} for code, person in SUSPECTS.items()]
    return {"version": VERSION, "people": people, "challenges": [
        {
            "id": "logic", "chapter": "1 · Logic & Proofs", "title": "Reconstruct the incident rule",
            "mission": "Check which accounts meet the three digital conditions before requesting a physical-location check.",
            "requires": INITIAL_RECORDS,
            "givens": ["P(x) means permission for research.pdf. T(x) means a verified login at 10:00–10:30 PM. W(x) means recorded Lab-PC2 activity.",
                       "For this exercise, 1 means the record matches the condition and 0 means it has no verified match. Physical-location evidence will be checked later."],
            "table": {"columns": ["Account", "P", "T", "W"], "rows": [[code, person["P"], person["T"], person["W"]] for code, person in SUSPECTS.items()]},
            "fields": [choice("rule", "Choose the rule requiring every digital condition", [
                ["any", "P(x) ∨ T(x) ∨ W(x)"], ["all", "P(x) ∧ T(x) ∧ W(x)"], ["implies", "P(x) → (T(x) ∨ W(x))"]]),
                {"key": "truth", "label": "Fill the output column for P ∧ T ∧ W", "type": "bits", "rows": [p["id"] for p in people], "columns": ["P ∧ T ∧ W"]},
                choice("contradiction", "An interview claims P(K) and ¬P(K). Can both be true together?", [["yes", "Yes"], ["no", "No"]])],
            "hints": ["A conjunction is true only when every input is true.", "Evaluate each row independently. A statement and its negation form a contradiction."],
            "reward": "Digital shortlist verified. Set reconstruction is now available.",
        },
        {
            "id": "structures", "chapter": "2 · Basic Structures", "title": "Build the candidate sets",
            "mission": "Reconstruct the shortlist with intersections and check the account-to-role function.",
            "requires": INITIAL_RECORDS,
            "givens": ["U = {A, S, O, L, K}. Build P, T and W from the source records.",
                       "Start with C₀ = U. For each new verified condition use Cₖ₊₁ = Cₖ ∩ Eₖ₊₁.",
                       "The directory assigns one role to each account. Ahmed is Administrator, Sara is Researcher, Omar and Lina are Students, and Khalid is Technician."],
            "fields": [accounts("c1", "C₁ = U ∩ P"), accounts("c2", "C₂ = C₁ ∩ T"), accounts("c3", "C₃ = C₂ ∩ W"),
                choice("function", "Is f(account) = its directory role a function on U?", [["yes", "Yes"], ["no", "No"]]),
                choice("injective", "Is that role function one-to-one?", [["yes", "Yes"], ["no", "No"]])],
            "hints": ["Keep an account in an intersection only when it belongs to both sets.", "A function assigns each input one output. One-to-one also requires different inputs to have different outputs."],
            "reward": "Candidate trace attached to your case. The filtering proof is now available.",
        },
        {
            "id": "induction", "chapter": "3 · Mathematical Induction", "title": "Prove the filtering rule",
            "mission": "Complete the proof that your filter keeps exactly the accounts satisfying the verified conditions at every step.",
            "requires": INITIAL_RECORDS,
            "givens": ["For any n ≥ 0, let E₁, …, Eₙ be verified evidence sets contained in U. Prove Cₖ = {x ∈ U | x satisfies E₁ through Eₖ} for 0 ≤ k ≤ n.",
                       "After your first three conditions, apply a further hypothetical verified set E₄ = U. This tests the invariant without inventing a new case fact."],
            "fields": [choice("base", "Base case · before any evidence, C₀ equals", [["empty", "∅"], ["U", "U"], ["first", "E₁"]]),
                choice("hypothesis", "Inductive hypothesis · assume Cₖ contains exactly the accounts satisfying", [["some", "At least one of the first k conditions"], ["all", "All of the first k conditions"], ["next", "Only condition k + 1"]]),
                choice("step", "Inductive step · define Cₖ₊₁ using", [["union", "Cₖ ∪ Eₖ₊₁"], ["intersection", "Cₖ ∩ Eₖ₊₁"], ["difference", "Cₖ ∖ Eₖ₊₁"]]),
                choice("reason", "Complete x ∈ Cₖ₊₁ ⇔", [["and", "x ∈ Cₖ AND x ∈ Eₖ₊₁"], ["or", "x ∈ Cₖ OR x ∈ Eₖ₊₁"]]),
                accounts("unchanged", "Apply the step to your shortlist when E₄ = U. Enter the resulting C₄")],
            "hints": ["The base case contains every account because no conditions have been applied.", "Use the definition of intersection for the inductive step. Intersecting any subset of U with U preserves that subset."],
            "reward": "Filtering proof verified. Plan your evidence review with counting.",
        },
        {
            "id": "counting", "chapter": "4 · Counting", "title": "Plan the evidence audit",
            "mission": "Size the audit before the Security Office releases its location verification. The six source records are distinct, including sealed records.",
            "requires": INITIAL_RECORDS,
            "givens": ["The repository has six source records. A review bundle is an unordered selection with no repeated record.",
                       "Count every possible subset, including the empty subset. Then count bundles containing exactly three records and unordered pairs of the five accounts.",
                       "These counts describe review choices. They do not measure how likely an account is to be responsible."],
            "fields": [number("subsets", "How many subsets can be selected from all six records?"),
                number("bundles", "How many different three-record review bundles are there?"),
                number("pairs", "How many different two-account comparison pairs are there?")],
            "hints": ["Each record has two choices, included or excluded. Use the product rule.", "For r unordered items chosen from n distinct items, C(n,r) = n! / (r!(n−r)!)."],
            "reward": "Audit plan verified. Location verification is now available in the Security Office.",
        },
        {
            "id": "relations", "chapter": "5 · Relations", "title": "Trace the file and test the alibi",
            "mission": "Encode access and device relations, compose the device-to-file trace, then apply the physical-location check to finish your case.",
            "requires": [*INITIAL_RECORDS, "location-verification"],
            "givens": ["Let R ⊆ U × {research.pdf, Lab-PC2}. An entry is 1 when a verified permission or device association exists, and 0 otherwise.",
                       "D relates accounts to Lab-PC2 activity. F = {(Lab-PC2, research.pdf)} records the incident file on that workstation. In F ∘ D, follow account → device → file.",
                       "Let N contain accounts with no verified physical alibi elsewhere. Finish with dom(F ∘ D) ∩ P ∩ T ∩ N under the direct-use assumption."],
            "fields": [{"key": "matrix", "label": "Fill the 0–1 matrix for R", "type": "bits", "rows": [p["id"] for p in people], "columns": ["research.pdf", "Lab-PC2"]},
                accounts("composition", "Which accounts appear in dom(F ∘ D)?"),
                accounts("final", "Which accounts remain in dom(F ∘ D) ∩ P ∩ T ∩ N?"),
                choice("scope", "What does the final singleton establish in this scenario?", [["guilt", "The person is proven guilty"], ["compatible", "One account is compatible with the verified records under the direct-use assumption"]])],
            "hints": ["Read each matrix entry as an ordered pair. Composition follows a shared middle element.", "After tracing account → Lab-PC2 → research.pdf, intersect the traced accounts with permission, time and location sets. A verified alibi elsewhere removes an account from this direct-use scenario."],
            "reward": "The full mathematical case is verified. Attach your work to the final report.",
        },
    ]}


def expected_answers():
    p, t, w, n = [clue_set(clue) for clue in CLUES[:4]]
    shortlist = p & t & w
    trace = {account for account, device in DEVICE_RELATION if device == "Lab-PC2"}
    return {
        "logic": {"rule": "all", "truth": [str(int(SUSPECTS[code]["P"] and SUSPECTS[code]["T"] and SUSPECTS[code]["W"])) for code in SUSPECTS], "contradiction": "no"},
        "structures": {"c1": sorted_codes(p), "c2": sorted_codes(p & t), "c3": sorted_codes(shortlist), "function": "yes", "injective": "no"},
        "induction": {"base": "U", "hypothesis": "all", "step": "intersection", "reason": "and", "unchanged": sorted_codes(shortlist)},
        "counting": {"subsets": 2 ** len(DOCUMENTS), "bundles": comb(len(DOCUMENTS), 3), "pairs": comb(len(SUSPECTS), 2)},
        "relations": {"matrix": [str(int((code, "research.pdf") in ACCESS_RELATION)) if col == 0 else str(int((code, "Lab-PC2") in DEVICE_RELATION)) for code in SUSPECTS for col in range(2)], "composition": sorted_codes(trace), "final": sorted_codes(trace & p & t & n), "scope": "compatible"},
    }


def check_fields(challenge, answers):
    expected = expected_answers()[challenge["id"]]
    if not isinstance(answers, dict) or set(answers) - set(expected):
        return [{"key": field["key"], "correct": False} for field in challenge["fields"]]
    checks = []
    for field in challenge["fields"]:
        value, target = answers.get(field["key"]), expected[field["key"]]
        if field["type"] == "accounts":
            correct = isinstance(value, list) and all(isinstance(item, str) for item in value) and len(value) == len(set(value)) and set(value) == set(target)
        elif field["type"] == "number":
            correct = isinstance(value, (str, int)) and not isinstance(value, bool) and bool(re.fullmatch(r"[0-9]{1,9}", str(value).strip())) and int(str(value).strip()) == target
        else:
            correct = value == target
        checks.append({"key": field["key"], "correct": correct})
    return checks


def verified_work(work, discovered):
    catalog = challenge_catalog()["challenges"]
    valid = []
    for challenge, entry in zip(catalog, work):
        if not isinstance(entry, dict) or entry.get("id") != challenge["id"] or entry.get("version") != VERSION:
            break
        if not set(challenge["requires"]).issubset(discovered):
            break
        if not all(check["correct"] for check in check_fields(challenge, entry.get("answers"))):
            break
        valid.append({"id": entry["id"], "version": VERSION, "answers": entry["answers"]})
    return valid


def worked_solution(challenge_id):
    answers = expected_answers()
    shown_set = lambda values: "{" + ", ".join(values) + "}"
    if challenge_id == "logic":
        return ["P ∧ T ∧ W has output " + ", ".join(answers["logic"]["truth"]) + " in the displayed account order.", "P ∧ ¬P is false for either truth value of P. Conflicting premises must be reviewed before drawing a conclusion."]
    if challenge_id == "structures":
        return [f"C₁ = {shown_set(answers['structures']['c1'])}, C₂ = {shown_set(answers['structures']['c2'])}, C₃ = {shown_set(answers['structures']['c3'])}.", "Every account has one role, so f is a function. Omar and Lina share the Student role, so f is not one-to-one."]
    if challenge_id == "induction":
        return ["Base · C₀ = U satisfies zero conditions.", "Assume Cₖ contains exactly the accounts satisfying all first k conditions. Then x ∈ Cₖ ∩ Eₖ₊₁ iff x satisfies those k conditions AND the next condition. Thus the claim holds for k + 1, and by induction for every processed k from 0 to n.", "For E₄ = U, C₄ = C₃ ∩ U = " + shown_set(answers["induction"]["unchanged"]) + "."]
    if challenge_id == "counting":
        return ["2⁶ = 64 subsets, including the empty subset.", "C(6,3) = 6! / (3!3!) = 20 bundles.", "C(5,2) = 5! / (2!3!) = 10 account pairs."]
    return ["Matrix rows encode membership in the file-permission and workstation relations.", "dom(F ∘ D) = " + shown_set(answers["relations"]["composition"]) + ".", "Intersecting the trace with P, T and N gives " + shown_set(answers["relations"]["final"]) + ". The verified physical alibi excludes the other traced account under the direct-use assumption. This supports account compatibility."]


def progress_status(work, discovered):
    valid = verified_work(work, discovered)
    return {"version": VERSION, "work": valid, "completed": [entry["id"] for entry in valid],
            "reviews": {entry["id"]: worked_solution(entry["id"]) for entry in valid}}


def grade_challenge(challenge_id, answers, work, discovered):
    challenges = challenge_catalog()["challenges"]
    challenge = next((item for item in challenges if item["id"] == challenge_id), None)
    if challenge is None:
        raise ValueError("Unknown mathematics challenge")
    valid = verified_work(work, discovered)
    index = challenges.index(challenge)
    if len(valid) < index:
        return {"correct": False, "blocked": True, "message": "Complete the preceding chapter challenges first."}
    if not set(challenge["requires"]).issubset(discovered):
        return {"correct": False, "blocked": True, "message": "Recover the source records listed for this challenge first."}
    checks = check_fields(challenge, answers)
    if not all(check["correct"] for check in checks):
        return {"correct": False, "checks": checks, "message": "Review the marked parts, then submit your work again. Your verified earlier chapters are saved."}
    new_work = [*valid[:index], {"id": challenge_id, "version": VERSION, "answers": answers}]
    # Rechecking an earlier correct answer preserves later verified work.
    if len(valid) > index:
        new_work = valid
    result = {"correct": True, "checks": checks, "message": challenge["reward"],
              "solution": worked_solution(challenge_id), "work": new_work}
    if len(new_work) == len(challenges):
        result["deduction"] = {"documents": [doc["id"] for doc in DOCUMENTS if doc["id"] in CORE_DOCUMENTS],
                               "expression": "dom(F ∘ D) ∩ P ∩ T ∩ N", "accounts": expected_answers()["relations"]["final"]}
    return result
