# Architecture note

## Proposed production flow

```text
Interview audio/video
      |
      v
Transcript + metadata
      |
      v
Insight generation agent
      |
      v
Evidence retrieval / citation builder
      |
      v
+------------------------------+
| Evidence Integrity Gate      |
| - semantic support           |
| - contradiction detection    |
| - numeric/entity provenance  |
| - sample diversity           |
| - policy thresholds          |
+------------------------------+
      |
  PASS | REVIEW | FAIL
      |
      +--> researcher review queue
      |
      v
Published insight/report/API
```

## Reliability principle

A generated insight should be treated like a production write operation:
it should not become authoritative merely because the model produced it.

The gate makes publication an explicit, observable decision with evidence lineage.

## Metrics I would expose

- unsupported-claim rate
- reviewer override rate
- evidence coverage per claim
- contradiction rate
- pass/review/fail by model version
- latency/cost per validated insight
- regression rate after model/prompt changes

Those metrics become release criteria for AI changes, not just dashboards.
