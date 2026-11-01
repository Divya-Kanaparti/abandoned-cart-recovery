# Database schema and relationships

Run `database/schema.sql` in MySQL 8.0+. Engine: InnoDB, charset utf8mb4. Every entity has a primary key and every required relationship is enforced by a foreign key.

- Customer 1:N Consent, Session, Cart, Order and SendAttempt.
- Session 1:N Cart (a cart belongs to one session; the session customer must match the cart customer).
- Cart 1:N CartLine, CartEvent, SendAttempt and Order; one Order per Cart in this synthetic implementation.
- Campaign 1:N MessageTemplate and SendAttempt; MessageTemplate 1:N SendAttempt. The generated campaign instances are paired 1:1 with a template and send, while the schema permits reuse.
- Customer N:M Campaign through SendAttempt; SendAttempt is the bridge carrying customer, cart, channel and campaign execution context.
- SendAttempt 1:N SendEvent.
- Order 1:0..1 Attribution; `UNIQUE(order_id)` prevents double credit.
- Order 1:N OrderLine.
- Customer/channel 1:N Consent history; effective dates preserve append-only opt-in/opt-out history.

Consent, cart, and send state changes are preserved in append-only event/history tables rather than replacing the prior event. Optional timestamps (`ended_at`, `abandoned_at`, `recovered_at`, `closed_at`, message `event_at`, consent `withdrawn_at`) are nullable until their lifecycle transition occurs. `ground_truth` and `anomalies` are separate evaluation artifacts and are not part of operational model features.
