# Case: Null — evaluation plan and blank instruments

Status: PREPARED. Human-participant study NOT CONDUCTED. No responses, learning gains, usability findings, or novelty claims are supplied.

## 1. Research question and scope

Can an interactive, rule-based investigation system correctly filter fictional candidates and explain each decision through discrete mathematical operations? Evaluate deterministic correctness separately from usability and educational comprehension. Do not measure or claim crime-prediction accuracy.

## 2. Case collection and independent baseline

Six synthetic cases contain five fictional identities and six independently selectable clues each. CASE-001 preserves Appendix A exactly. BENCH-EMPTY, BENCH-MULTIPLE, BENCH-UNKNOWN, BENCH-CONFLICT and BENCH-DISPUTED are explicitly additional evaluation fixtures. They do not revise the research's case records.

The independent baseline in backend/benchmarks.py is a manually specified six-column Boolean table encoded as bitmasks. Bit 0 represents E1 through bit 5 representing E6. Unknown and disputed columns are marked ignored; the contradiction fixture separately requires NOT P. The baseline does not call the inference engine to determine its expected candidates.

For all 64 selections in each case, compare expected and actual candidate sets, require valid source-linked exclusion reasons, suspend conclusions on unsatisfiable mandatory conditions, and verify that unknown/disputed facts are not silently treated as false. The full per-configuration expected/actual results are written to automated-results.json and automated-results.csv by `python -m backend.benchmarks`.

## 3. Automated acceptance criteria

| Measure | Operational definition | Success condition |
| --- | --- | --- |
| Candidate-set correctness | Exact ordered-set comparison with the independent manual baseline for every configuration | All 384 patterns match |
| Traceability | Every exclusion names an applied verified mandatory clue or explicit test constraint, source and rule | Every exclusion traceable |
| Contradiction behavior | SymPy detects P AND NOT P; result unresolved rather than a forced candidate | No invented conclusion |
| Unknown/disputed handling | Ignored conditions remain visible; candidates unchanged by an unknown/provisional-only selection | Unknown never silently false |
| Research example | Verify original records, all six sets, literal intersections, both logic rules and exact relations | Exact Appendix A match |

These are algorithmic checks, not a substitute for participant testing or independent validation of real evidence.

## 4. Voluntary participant procedure

Before recruitment, follow the institution's applicable classroom/research requirements. Explain that participation is voluntary, unrelated to grades, and may stop at any time. Use anonymous session codes; do not collect names, student numbers, real account data, real evidence, or accusations. Obtain appropriate permission before collecting or sharing responses. Keep exports local unless a participant has agreed to a specific use.

Record the app version, session code, date, prior exposure to discrete mathematics, permitted assistance, and whether the Appendix A worked example was shown. Do not invent missing observations. Keep raw observations separate from interpretation.

## 5. Participant tasks

1. Open the research case, inspect the scope and one evidence source's metadata.
2. Select and deselect clues; explain the resulting candidate-set change.
3. Explain one inclusion and one exclusion, citing the source, predicate and set operation.
4. Inspect a profile; drag a board card and confirm the mathematical result is unchanged.
5. Open the resource-relations view and identify a “can access” or “activity on” pair.
6. Distinguish an empty matching set from mutually contradictory mandatory statements.
7. Show an unknown or disputed record and explain why it is not an automatic exclusion condition.
8. Explain the induction invariant, counts, and Boolean interpretation of the matrix.
9. Export a case report and find its selected evidence, source metadata, relation links, operation trace and candidate list.

Observe task completion, assistance, navigation difficulties, and the participant's own explanation. If recording time, use an actual stopwatch or timestamps and clearly state whether reading time and assistance are included. No completion-time results are currently claimed.

## 6. Objective scoring rubric

Score each of the following five areas 0, 1 or 2. Leave “not assessed” blank rather than entering a zero for an unobserved task. A total out of 10 may be calculated only if all five areas were actually assessed.

| Area | 0 — not demonstrated | 1 — partial / assisted | 2 — independent and correct |
| --- | --- | --- | --- |
| Candidate reasoning | Cannot connect retained/excluded identities to conditions | Correct idea with a missing condition or assistance | Correctly explains conjunction and intersection using the selected facts |
| Traceability | Cannot identify a source or operation | Identifies only a source or operation, or needs help | Cites source, required predicate, operation and decision correctly |
| Contradiction | Treats conflicting mandatory claims as a forced conclusion | Recognizes a conflict but explanation incomplete | Explains P AND NOT P, unsatisfiability and suspended conclusion; distinguishes NO_MATCH |
| Unknown information | Treats absent/unknown data as automatically false | Recognizes uncertainty with prompting | Explains provisional visibility, no automatic filtering, and the synthetic closed-world assumption |
| Interface usability | Cannot complete the inspection/export tasks | Completes with assistance or notable difficulty | Independently selects/deselects, inspects, moves cards and exports a readable report |

## 7. Blank session record

- Anonymous session code: __________
- Actual session date and app version: __________
- Voluntary agreement confirmed: not recorded / yes / no
- Prior exposure and assistance conditions: __________
- Candidate reasoning score: not assessed / 0 / 1 / 2
- Traceability score: not assessed / 0 / 1 / 2
- Contradiction score: not assessed / 0 / 1 / 2
- Unknown-information score: not assessed / 0 / 1 / 2
- Interface-usability score: not assessed / 0 / 1 / 2
- Actual observed completion times, if measured: __________
- Navigation problems and assistance supplied: __________
- Participant feedback in their own words: __________
- Evaluator interpretation, separated from raw observations: __________

The Evaluation tab provides a local worksheet with all scores initially “Not assessed.” Exporting a worksheet does not create an aggregate study result.

## 8. Reporting without overclaiming

Report the number actually recruited, withdrawals, missing observations, exact task/rubric definitions and actual scores. Summarize limitations, prior familiarity, assistance and potential bias. Do not infer improved learning without an appropriate study design and evidence. Correct filtering does not establish evidence authenticity, personal identification, forensic admissibility, real-world attribution accuracy or project novelty.
