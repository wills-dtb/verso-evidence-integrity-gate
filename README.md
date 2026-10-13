# Verso Evidence Integrity Gate

A small runnable prototype for a problem adjacent to Verso's product:

> How do you stop an AI research agent from turning plausible synthesis into an
> unsupported business insight?

Verso's public product positioning emphasizes fast, evidence-backed qualitative
research. This prototype inserts a deterministic quality gate between synthesis
and publication.

It checks whether a generated insight:
- cites enough distinct respondents,
- is grounded in the cited excerpts,
- contains suspicious numeric claims not present in the evidence,
- over-generalises from a very small sample,
- and preserves an auditable trail from conclusion -> respondent evidence.

The output is `PASS`, `REVIEW`, or `FAIL`.

## Why this matters

When AI-generated research is used for product/marketing decisions, the dangerous
failure mode is not always an obviously wrong answer. It is a *plausible* claim
that outruns its evidence.

A production-grade system should make it cheap to ask:
1. What evidence supports this conclusion?
2. How many independent respondents support it?
3. Is there contradictory evidence?
4. Has the system introduced a number or fact that nobody actually said?
5. Should this insight ship automatically or require researcher review?

## Architecture

`Research Agent -> Proposed Insight -> Evidence Integrity Gate -> PASS / REVIEW / FAIL`

Each decision includes:
- support score,
- cited respondent count,
- unsupported number detection,
- over-generalisation detection,
- exact evidence IDs,
- audit hash.

The demo is intentionally deterministic. It does **not** call an LLM.

## Run

Requires Python 3.10+ and no third-party packages.

```bash
python app.py sample_study.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Example

Input claim:

> Most users find onboarding confusing and abandon setup within 10 minutes.

If the cited evidence mentions confusion but never mentions `10 minutes`, the
gate flags the introduced numeric detail for review/failure rather than allowing
a polished but unsupported insight into the report.

## Deliberately left out for the 2–3 hour constraint

- multilingual semantic entailment,
- contradiction classification,
- calibrated confidence thresholds,
- embedding retrieval,
- model-based evidence ranking,
- PII redaction,
- per-client policy configuration,
- reviewer UI,
- persistence/observability,
- statistical representativeness checks.

## Production version

I would split this into four layers:

1. **Evidence retrieval** — multilingual embeddings + reranking over transcript spans.
2. **Entailment** — NLI/LLM judge that scores support, contradiction and ambiguity.
3. **Policy engine** — configurable thresholds by study type and decision risk.
4. **Audit layer** — immutable claim/evidence/version lineage with reviewer actions.

I would also evaluate the evaluator itself with a labelled dataset of supported,
partially-supported, contradicted and hallucinated insights, then run that eval
suite in CI whenever prompts, models or retrieval logic change.

## Why this is a leadership rather than "QA" artifact

The point is not to add tests after the product is built. It is to make
trustworthiness an architectural property of an AI-native workflow:
observable, configurable, auditable and safe to scale across enterprise customers.
