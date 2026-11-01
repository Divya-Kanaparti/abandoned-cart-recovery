# Synthetic data generation

Seed: `20261022`; fixed reference time: `2026-10-30T12:00:00`. The same deterministic generator powers both profiles.

| Profile | Customers | Carts | Abandoned-at-evaluation | Send attempts |
|---|---:|---:|---:|---:|
| starter | 1,000 | 1,000 | 400 | 200 |
| full | 50,000 | 50,000 | 20,000 | 10,000 |

Each campaign row is a scheduled campaign execution instance paired with one send attempt; A/B/C encode the reusable 1h, 6h and 24h channel/timing variants. The full profile produces 10,000 campaign instances and 10,000 send attempts. Rows are generated in dependency order: customers/consent, sessions/carts/cart lines/events, campaigns/templates, orders/order lines, sends/send events/audit decisions, then attribution and ground truth. Derived totals are calculated from line items. The generator emits CSV and JSON for every table, a generation report and SHA-256 checksum manifest. Four negative scenarios are separate labelled fixtures in `anomalies.csv/json` and do not contaminate baseline feature tables. No external personal data is used; all data is synthetic (`example.test` domains and reserved synthetic contact values).
