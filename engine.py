"""Case: Null — deterministic discrete-mathematics engine, Appendix A.

All data below are synthetic. Candidate compatibility is NOT attribution of guilt.
"""
from __future__ import annotations
from itertools import combinations
from math import comb
from typing import Any
from sympy import And, Not, Symbol, satisfiable

SUSPECTS = {
    "A": {"name":"Ahmed", "role":"Administrator", "last_login":"5:35 PM", "P":1,"T":0,"W":0,"N":1,"active":1,"training":1},
    "S": {"name":"Sara", "role":"Researcher", "last_login":"10:14 PM", "P":1,"T":1,"W":1,"N":0,"active":1,"training":1},
    "O": {"name":"Omar", "role":"Student", "last_login":"10:09 PM", "P":0,"T":1,"W":0,"N":1,"active":1,"training":0},
    "L": {"name":"Lina", "role":"Student", "last_login":None, "P":0,"T":0,"W":0,"N":1,"active":1,"training":1},
    "K": {"name":"Khalid", "role":"Technician", "last_login":"10:21 PM", "P":1,"T":1,"W":1,"N":1,"active":1,"training":1},
}
CLUES = [
    {"id":"E1","label":"Research file permission","description":"Authorized to open research.pdf","field":"P"},
    {"id":"E2","label":"Incident-time login","description":"Matching login from 10:00–10:30 PM","field":"T"},
    {"id":"E3","label":"Lab-PC2 workstation activity","description":"Associated with activity on Lab-PC2","field":"W"},
    {"id":"E4","label":"Validated physical alibi","description":"Not excluded by a verified alibi elsewhere","field":"N"},
    {"id":"E5","label":"Active account","description":"Account active in the fictional case","field":"active"},
    {"id":"E6","label":"Laboratory access training","description":"Completed laboratory access training","field":"training"},
]
ACCESS_RELATION = [("A","research.pdf"),("S","research.pdf"),("K","research.pdf"),("S","draft.txt"),("O","draft.txt")]
DEVICE_RELATION = [("S","Lab-PC2"),("K","Lab-PC2")]
CLUE_IDS = [c['id'] for c in CLUES]

def clue_set(clue:dict) -> set[str]:
    return {code for code, suspect in SUSPECTS.items() if suspect[clue['field']] == 1}

def sorted_codes(codes):
    return [code for code in SUSPECTS if code in codes]

def analyze(selected: list[str] | None = None, conflicting: bool = False, unknown: bool = False) -> dict[str,Any]:
    selected = selected or []
    if len(selected) != len(set(selected)) or any(c not in CLUE_IDS for c in selected):
        raise ValueError("Selected clues must be unique identifiers E1–E6")
    ordered = [c for c in CLUES if c['id'] in selected]
    universe = set(SUSPECTS)
    remaining = set(universe)
    trace = [{"clue":"C0", "label":"All identities", "candidates":sorted_codes(remaining), "operation":"C₀ = U"}]
    exclusions = []
    for index, clue in enumerate(ordered,1):
        matched = clue_set(clue)
        excluded = remaining - matched
        for code in sorted_codes(excluded):
            exclusions.append({"suspect":code,"clue":clue['id'],"reason":clue['description']})
        remaining &= matched
        trace.append({"clue":clue['id'],"label":clue['label'],"candidates":sorted_codes(remaining),"operation":f"C{index} = C{index-1} ∩ {clue['id']}"})
    # The optional deliberately incompatible verified constraint says NOT P, while E1 says P.
    # SymPy detects unsatisfiability, independently of candidate-set intersection.
    P = Symbol('P')
    mandatory_constraints = ([P] if 'E1' in selected else []) + ([Not(P)] if conflicting else [])
    contradiction = bool(mandatory_constraints) and satisfiable(And(*mandatory_constraints)) is False
    if conflicting and not contradiction:
        matched = {code for code,s in SUSPECTS.items() if not s['P']}
        excluded = remaining - matched
        for code in sorted_codes(excluded):
            exclusions.append({"suspect":code,"clue":"X1","reason":"Injected test requires NOT P"})
        remaining &= matched
        trace.append({"clue":"X1","label":"Injected NOT P constraint", "candidates":sorted_codes(remaining),"operation":"C ← C ∩ ¬P"})
    # Every unknown/provisional record is shown but never used as a verified exclusion.
    matrix = [{"id":code,"name":s['name'],"P":s['P'],"T":s['T'],"W":s['W'],"N":s['N'],"and_result":int(all(s[f] for f in ('P','T','W','N')))} for code,s in SUSPECTS.items()]
    clue_matches = {c['id']:sorted_codes(clue_set(c)) for c in CLUES}
    return {
        "selected":selected,"candidates":None if contradiction else sorted_codes(remaining),
        "contradiction":contradiction,"conflicting_test":conflicting,
        "warning":"Contradictory verified conditions P and NOT P. Conclusion suspended." if contradiction else ("No candidate matches every selected clue; inspect premises." if not remaining else None),
        "unknown_record": {"status":"UNKNOWN","description":"Unverified possible remote login; excluded from mandatory filtering"} if unknown else None,
        "trace":trace,"exclusions":exclusions,"matrix":matrix,"clue_matches":clue_matches,
        "logic":"PhysicalCandidate(x) = P(x) ∧ T(x) ∧ W(x) ∧ N(x)",
        "quantifiers":{"exists_full_candidate":any(row['and_result'] for row in matrix),"all_full_candidates":all(row['and_result'] for row in matrix)},
        "counting":{"all_selection_patterns":2**6,"choose_three_clues":comb(6,3),"two_suspect_pairs":comb(5,2)},
        "relations":{"file_access":[list(r) for r in ACCESS_RELATION],"device_activity":[list(r) for r in DEVICE_RELATION]},
        "induction":{"base":"C₀ = U","hypothesis":"After k clues, Cₖ contains exactly those satisfying the first k clues.","step":"Cₖ₊₁ = Cₖ ∩ Eₖ₊₁; therefore all k+1 conditions hold.","limitation":"Correctness depends on the encoded verified premises."},
        "case_limit":"Fictional classroom scenario: direct physical use of Lab-PC2 assumed; remote access excluded. Account activity is not proof of the person operating the workstation. Remaining candidates are not proven guilty."
    }

def public_case():
    return {"id":"CASE-001","name":"The Midnight Copy","incident_time":"10:25 PM","computer":"Lab-PC2","file":"research.pdf","suspects":[{"id":id,**s} for id,s in SUSPECTS.items()],"clues":[{**c,"matches":sorted_codes(clue_set(c))} for c in CLUES],"files":["research.pdf","draft.txt"],"devices":["Lab-PC2","Office-PC"]}
