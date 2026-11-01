# Validation and acceptance coverage

Run `python generator/validation.py --input data/starter --output data/starter/validation` (or substitute `data/full`). The validator checks:

- Required primary keys, uniqueness, and all declared foreign keys.
- Enumerated values and parseable timestamps.
- Customer/session consistency, session date ordering, cart lifecycle timestamps and the 60-minute abandonment boundary.
- Cart and order arithmetic reconciliation from their line records.
- Channel-specific consent at send time, campaign/template channel agreement, purchase-before-send suppression, duplicate cart/campaign sends, 3-per-channel rolling 7-day frequency cap and 24-hour minimum interval.
- Chronological send events, no events before send, attribution eligibility/window/revenue, and one attribution per order.
- Ground-truth references and labelled anomaly fixture counts.

A clean baseline reports `PASS_WITH_LABELLED_ANOMALIES`: the four negative scenarios are isolated in `anomalies.csv/json`, not silently injected into operational baseline tables. A nonzero `validation_issue_count` is a failure and must be resolved before acceptance. `validation_issues.csv` and `validation_summary.json` contain actionable findings.
