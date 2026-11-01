# Data dictionary and validation contract

All timestamps are ISO-8601 local demo timestamps (`YYYY-MM-DD HH:MM:SS`); production systems should use UTC with an explicit timezone. Monetary values are INR with two decimal places. Boolean CSV values are `true`/`false`. Empty strings represent nullable values. IDs are immutable and unique within their entity.

| Entity / field | Type | Req. | Allowed values / units | Uniqueness | Validation |
|---|---|---:|---|---|---|
| Customer.customer_id | string | yes | `CUS-` + six digits | PK | Must match `CUS-\\d{6}` |
| Customer.first_name, last_name | string | yes | synthetic names | no | Non-empty; synthetic only |
| Customer.email | string | yes | `.example.test` address | unique | Valid email-shaped synthetic address |
| Customer.phone | string | yes | E.164-like synthetic number | no | `+` and digits only |
| Customer.email_valid, phone_valid | boolean | yes | true/false | no | Parsed as booleans |
| Customer.created_at | datetime | yes | timestamp | no | Must parse; not after reference time |
| Consent.consent_id | string | yes | `CON-<customer>-<channel>-NN` | PK | Immutable; FK to Customer |
| Consent.customer_id | string | yes | Customer ID | no | FK; parent must exist |
| Consent.channel | enum | yes | EMAIL, SMS | no | Channel-specific consent |
| Consent.status | enum | yes | OPTED_IN, OPTED_OUT, UNKNOWN | no | Latest effective record controls eligibility |
| Consent.effective_at | datetime | yes | timestamp | no | Must parse; records ordered by effective time |
| Consent.withdrawn_at | datetime | no | timestamp | no | Must be >= effective_at; withdrawal must be OPTED_OUT |
| Consent.source | enum/string | yes | CHECKOUT, PREFERENCE_CENTER | no | Provenance recorded |
| Session.session_id | string | yes | `SES-` + seven digits | PK | FK customer exists |
| Session.customer_id | string | yes | Customer ID | no | FK to Customer |
| Session.device_type | enum | yes | DESKTOP, MOBILE, TABLET | no | Allowed enum |
| Session.started_at, ended_at | datetime | started required; ended optional | timestamp | no | End >= start |
| Cart.cart_id | string | yes | `CART-2026-` + six digits | PK | Immutable; FK customer/session |
| Cart.customer_id, session_id | string | yes | parent IDs | no | Both FKs; session/customer must agree |
| Cart.status | enum | yes | ACTIVE, ABANDONED, RECOVERY_PENDING, RECOVERED, EXPIRED, SUPPRESSED, PURCHASED | no | Must agree with lifecycle timestamps and orders |
| Cart.currency | char(3) | yes | INR | no | ISO-style currency code |
| Cart.cart_total | decimal(12,2) | yes | INR | no | Equals sum(quantity * unit_price) from CartLine |
| Cart.created_at, last_activity_at | datetime | yes | timestamp | no | created <= last activity |
| Cart.abandoned_at, recovered_at, closed_at | datetime | no | timestamp | no | Abandonment = last activity + 60 min; recovery >= creation |
| CartLine.cart_line_id | string | yes | `CL-<cart-sequence>-NN` | PK | FK to Cart |
| CartLine.cart_id | string | yes | Cart ID | no | FK to Cart |
| CartLine.sku, product_name | string | yes | synthetic catalog | no | Non-empty |
| CartLine.quantity | integer | yes | count | no | > 0 |
| CartLine.unit_price | decimal(10,2) | yes | INR | no | >= 0 |
| CartLine.updated_at | datetime | yes | timestamp | no | Must parse; within cart lifecycle |
| Campaign.campaign_id | string | yes | `CMP-2026-` + six digits | PK | Immutable |
| Campaign.campaign_name, target_audience | string | yes | descriptive text | no | Non-empty |
| Campaign.channel | enum | yes | EMAIL, SMS | no | Must match template/send channel |
| Campaign.variant | enum | yes | A, B, C | no | A=1h, B=6h, C=24h recovery schedule |
| Campaign.scheduled_at, created_at | datetime | yes | timestamp | no | Must parse; created <= scheduled |
| Campaign.status | enum | yes | DRAFT, SCHEDULED, RUNNING, COMPLETED, CANCELLED | no | Allowed lifecycle state |
| MessageTemplate.template_id | string | yes | `TPL-` + six digits | PK | FK to Campaign |
| MessageTemplate.campaign_id | string | yes | Campaign ID | no | FK; channel must match campaign |
| MessageTemplate.channel | enum | yes | EMAIL, SMS | no | EMAIL/SMS only |
| MessageTemplate.subject | string | no | text | no | Nullable for SMS |
| MessageTemplate.body | string | yes | text with supported tokens | no | Non-empty; tokens documented in template |
| SendAttempt.send_id | string | yes | `SEND-2026-` + six digits | PK | Immutable |
| SendAttempt.campaign_id, template_id, customer_id, cart_id | string | yes | parent IDs | no | All FKs; customer/cart must agree |
| SendAttempt.channel | enum | yes | EMAIL, SMS | no | Must match campaign and template |
| SendAttempt.status | enum | yes | SEND_ATTEMPTED, SENT, DELIVERED, BOUNCED, OPENED, CLICKED, FAILED, SUPPRESSED | no | Must agree with events and suppression reason |
| SendAttempt.attempted_at | datetime | yes | timestamp | no | After abandonment threshold; before purchase |
| SendAttempt.event_at | datetime | no | timestamp | no | Must be >= attempted_at |
| SendAttempt.failure_reason, recovery_link | string | no | reason / synthetic URL | no | Suppressed attempts carry reason |
| SendEvent.event_id | integer | yes | sequence | PK | FK to SendAttempt |
| SendEvent.send_id | string | yes | Send ID | no | FK; timestamps nondecreasing |
| SendEvent.event_type | enum | yes | SENT, DELIVERED, OPENED, CLICKED, BOUNCED | no | Legal progression only |
| SendEvent.event_at | datetime | yes | timestamp | no | >= attempted_at |
| Order.order_id | string | yes | `ORD-2026-` + six digits | PK | Immutable |
| Order.customer_id, cart_id | string | yes | parent IDs | customer/cart pair | FKs; one order per cart |
| Order.order_status | enum | yes | COMPLETED, CANCELLED, REFUNDED | no | Allowed order state |
| Order.order_total | decimal(12,2) | yes | INR | no | Equals sum(OrderLine amounts) |
| Order.ordered_at | datetime | yes | timestamp | no | >= cart creation |
| OrderLine.order_line_id | string | yes | `OL-NNNNNN-NN` | PK | FK to Order |
| OrderLine.order_id | string | yes | Order ID | no | FK |
| OrderLine.sku, product_name | string | yes | synthetic catalog | no | Non-empty |
| OrderLine.quantity | integer | yes | count | no | > 0 |
| OrderLine.unit_price | decimal(10,2) | yes | INR | no | >= 0 |
| Attribution.attribution_id | integer | yes | sequence | PK | Unique per attribution record |
| Attribution.order_id | string | yes | Order ID | unique | Exactly zero or one attribution per order |
| Attribution.customer_id, cart_id, campaign_id, send_id | string | yes | parent IDs | no | FKs and consistent with order/send |
| Attribution.model | enum | yes | LAST_TOUCH_7D | no | Deterministic 7-day model |
| Attribution.attributed_at | datetime | yes | interaction timestamp | no | Between send interaction and order, within 7 days |
| Attribution.attributed_revenue | decimal(12,2) | yes | INR | no | Equals order_total, counted once |
| Attribution.reason | string | yes | explanation | no | Records selected interaction type |

## Supporting traceability tables

`cart_events` is append-only cart lifecycle history; `audit_decisions` stores each eligible/suppressed decision and reason; `anomalies` and `ground_truth` are separate labelled evaluation artifacts. `order_lines` and `send_events` preserve line-level and message-event history. `ground_truth` is never joined into operational input features.
