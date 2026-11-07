# M1 - Query Labelling Protocol

Dataset: `datasets/queries/labelled_queries.csv` (400 questions, seed 42, fully reproducible).

## Columns
`query_id, question, route, subtype, gold_sql, gold_rag_source, gold_answer`

## Route definitions
| Route | Meaning | Gold fields | Count |
|---|---|---|---|
| RAG | General educational/concept question answered from documents | `gold_rag_source`, key points in `gold_answer` | 100 |
| SQL | Needs only student/faculty/course records from the database | `gold_sql` + executed result in `gold_answer` | 100 |
| BOTH | Needs a database fact AND a document rule/concept to answer | `gold_sql` + `gold_rag_source` + result and rule | 80 |
| NOT-FOUND | In-domain request for a record that does not exist in the DB | `gold_sql` (returns 0 rows) | 60 |
| OUT-OF-SCOPE | Outside the assistant's domain, or an unsupported/unsafe operation | none | 60 |

## Labelling rules (decision order)
1. Is the request about the college's academic data or education concepts? If not -> **OUT-OF-SCOPE**.
2. Does it ask to modify data, access admin/credentials, or other institutions' data? -> **OUT-OF-SCOPE** (subtype `unsafe-write-or-admin` / `other-institutions`). The system is read-only.
3. Does it refer to a student/course/faculty/department/semester that does not exist (or a student not enrolled in that course)? -> **NOT-FOUND**.
4. Does it need only DB values? -> **SQL**. Only document knowledge? -> **RAG**. Both a DB value and a rule/concept? -> **BOTH**.
5. One question = exactly one route. Questions that mix a record lookup with a rule/concept are always BOTH.

NOT-FOUND vs OUT-OF-SCOPE: *"Show marks of 25BQ1A9999"* is a valid academic request with no matching record (NOT-FOUND); *"Tell me today's cricket score"* is not an academic request at all (OUT-OF-SCOPE).

## Gold-answer verification
Every gold SQL is executed against `data/generated/synthetic_education.db` during generation:
SQL/BOTH queries must return a non-empty result; NOT-FOUND queries must return zero rows.
Only `SELECT` statements are used. `tests/M1/test_dataset.py` re-checks this.

## Regulations used by BOTH questions
`documents/academic_regulations.md` (synthetic rules: 75% attendance, pass mark 40, grading scale,
supplementary, revaluation, promotion). Ingest it into the RAG knowledge base so BOTH questions are answerable.

## Generic subtypes
61 subtypes (e.g. `marks-lookup`, `attendance-eligibility`, `missing-student`, `unsafe-write-or-admin`) are in the `subtype` column for error analysis.
