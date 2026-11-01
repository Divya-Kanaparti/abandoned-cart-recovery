import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

if __package__:
    from .configuration import PROFILES, REFERENCE_TIME, SEED
else:
    from configuration import PROFILES, REFERENCE_TIME, SEED

PRODUCTS = [
    ("SKU-100", "Wireless Mouse", 799),
    ("SKU-101", "Mechanical Keyboard", 2499),
    ("SKU-102", "USB-C Hub", 1599),
    ("SKU-103", "Laptop Stand", 1199),
    ("SKU-104", "Noise Cancelling Headphones", 4999),
    ("SKU-105", "Webcam", 2199),
    ("SKU-106", "Portable SSD", 3499),
    ("SKU-107", "Bluetooth Speaker", 1899),
]
FIRST = ["Aarav", "Diya", "Ishita", "Rohan", "Ananya", "Vihaan", "Meera", "Kabir", "Sana", "Arjun"]
LAST = ["Sharma", "Reddy", "Patel", "Rao", "Khan", "Iyer", "Gupta", "Nair", "Das", "Verma"]
CHANNELS = ("EMAIL", "SMS")
ABANDONMENT_MINUTES = 60
ATTRIBUTION_DAYS = 7
CAMPAIGN_DELAYS = (1, 6, 24)

TABLE_FIELDS = {
    "customers": ["customer_id", "first_name", "last_name", "email", "phone", "email_valid", "phone_valid", "created_at"],
    "consents": ["consent_id", "customer_id", "channel", "status", "effective_at", "withdrawn_at", "source"],
    "sessions": ["session_id", "customer_id", "device_type", "started_at", "ended_at"],
    "carts": ["cart_id", "customer_id", "session_id", "status", "currency", "cart_total", "created_at", "last_activity_at", "abandoned_at", "recovered_at", "closed_at"],
    "cart_lines": ["cart_line_id", "cart_id", "sku", "product_name", "quantity", "unit_price", "updated_at"],
    "campaigns": ["campaign_id", "campaign_name", "channel", "variant", "target_audience", "scheduled_at", "status", "created_at"],
    "message_templates": ["template_id", "campaign_id", "channel", "subject", "body"],
    "send_attempts": ["send_id", "campaign_id", "template_id", "customer_id", "cart_id", "channel", "status", "attempted_at", "event_at", "failure_reason", "recovery_link"],
    "send_events": ["event_id", "send_id", "event_type", "event_at"],
    "orders": ["order_id", "customer_id", "cart_id", "order_status", "order_total", "ordered_at"],
    "order_lines": ["order_line_id", "order_id", "sku", "product_name", "quantity", "unit_price"],
    "attributions": ["attribution_id", "order_id", "customer_id", "cart_id", "campaign_id", "send_id", "model", "attributed_at", "attributed_revenue", "reason"],
    "audit_decisions": ["decision_id", "customer_id", "cart_id", "channel", "decision", "reason_code", "detail", "decided_at"],
    "cart_events": ["event_id", "cart_id", "event_type", "event_at", "details"],
    "ground_truth": ["cart_id", "expected_abandoned_status", "expected_consent_eligible", "expected_suppression_decision", "expected_campaign_eligible", "expected_attribution", "expected_anomaly_classification", "expected_revenue_attribution"],
    "anomalies": ["issue_type", "ground_truth", "expected_decision", "actual_decision", "affected_entity_id", "description", "detected_at"],
}


def _dt(value):
    return datetime.fromisoformat(value)


def _write_table(output, name, rows):
    path = output / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=TABLE_FIELDS[name])
        writer.writeheader()
        writer.writerows(rows)
    (output / f"{name}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


def _latest_consent(consents, customer_id, channel, at):
    eligible = [
        row for row in consents[(customer_id, channel)]
        if _dt(row["effective_at"]) <= at
    ]
    return max(eligible, key=lambda row: row["effective_at"], default=None)


def _money(value):
    return f"{value:.2f}"


def _sql_literal(value):
    if value is None or value == "":
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def _write_sql_seed(output, tables):
    # The SQL schema uses AUTO_INCREMENT surrogate keys for these entities;
    # omit their synthetic CSV identifiers while preserving the source CSVs.
    auto_ids = {
        "consents": {"consent_id"}, "cart_lines": {"cart_line_id"},
        "order_lines": {"order_line_id"}, "send_events": {"event_id"},
        "attributions": {"attribution_id"}, "audit_decisions": {"decision_id"},
        "cart_events": {"event_id"}, "anomalies": set(),
    }
    table_map = {"anomalies": "anomaly_issues"}
    order = ["customers", "consents", "sessions", "carts", "cart_lines",
             "campaigns", "message_templates", "send_attempts", "orders",
             "order_lines", "send_events", "attributions", "audit_decisions",
             "cart_events", "anomalies"]
    path = output / "seed.sql"
    with path.open("w", encoding="utf-8", newline="\n") as sql:
        sql.write("-- Generated synthetic seed data. Load after database/schema.sql.\n")
        sql.write("SET FOREIGN_KEY_CHECKS=0;\nSTART TRANSACTION;\n")
        for name in order:
            rows = tables.get(name, [])
            if not rows:
                continue
            columns = [c for c in rows[0] if c not in auto_ids.get(name, set())]
            db_table = table_map.get(name, name)
            quoted_cols = ", ".join(f"`{c}`" for c in columns)
            for start in range(0, len(rows), 500):
                batch = rows[start:start + 500]
                sql.write(f"INSERT INTO `{db_table}` ({quoted_cols}) VALUES\n")
                values = []
                for row in batch:
                    values.append("(" + ", ".join(_sql_literal(row.get(c)) for c in columns) + ")")
                sql.write(",\n".join(values) + ";\n")
        sql.write("COMMIT;\nSET FOREIGN_KEY_CHECKS=1;\n")


def generate(profile, output):
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    config = PROFILES[profile]
    customer_count = config["customers"]
    cart_count = config["carts"]
    abandoned_target = config["abandoned"]
    send_count = config["sends"]
    if customer_count < 1 or cart_count < 1 or not 0 <= abandoned_target <= cart_count:
        raise ValueError("Profile counts must be positive and abandoned carts cannot exceed total carts")
    if send_count > abandoned_target:
        raise ValueError("Send attempts cannot exceed abandoned-cart candidates")

    rng = random.Random(SEED)
    reference = _dt(REFERENCE_TIME)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    customers, consents, sessions, carts, cart_lines = [], [], [], [], []
    campaigns, templates, sends, send_events = [], [], [], []
    orders, order_lines, attributions, audit_decisions, cart_events = [], [], [], [], []
    ground_truth = []
    consent_index = defaultdict(list)
    cart_line_index = defaultdict(list)
    cart_event_counter = 0

    for index in range(1, customer_count + 1):
        customer_id = f"CUS-{index:06d}"
        first_name, last_name = rng.choice(FIRST), rng.choice(LAST)
        customers.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{index}@example.test",
            "phone": f"+9199{index:07d}",
            "email_valid": True,
            "phone_valid": True,
            "created_at": (reference - timedelta(days=rng.randint(30, 500))).isoformat(sep=" "),
        })
        for channel in CHANNELS:
            status = rng.choices(["OPTED_IN", "OPTED_OUT", "UNKNOWN"], [0.72, 0.18, 0.10])[0]
            effective = reference - timedelta(days=rng.randint(5, 180))
            records = [{
                "consent_id": f"CON-{index:06d}-{channel}-01",
                "customer_id": customer_id,
                "channel": channel,
                "status": status,
                "effective_at": effective.isoformat(sep=" "),
                "withdrawn_at": "",
                "source": "CHECKOUT" if status == "OPTED_IN" else "PREFERENCE_CENTER",
            }]
            if status == "OPTED_IN" and rng.random() < 0.15:
                withdrawn = reference - timedelta(hours=rng.randint(1, 48))
                if withdrawn > effective:
                    records.append({
                        "consent_id": f"CON-{index:06d}-{channel}-02",
                        "customer_id": customer_id,
                        "channel": channel,
                        "status": "OPTED_OUT",
                        "effective_at": withdrawn.isoformat(sep=" "),
                        "withdrawn_at": withdrawn.isoformat(sep=" "),
                        "source": "PREFERENCE_CENTER",
                    })
            consents.extend(records)
            consent_index[(customer_id, channel)].extend(records)

    for index in range(1, cart_count + 1):
        customer_id = f"CUS-{rng.randint(1, customer_count):06d}"
        cart_id = f"CART-2026-{index:06d}"
        session_id = f"SES-{index:07d}"
        is_abandoned_candidate = index <= abandoned_target
        if is_abandoned_candidate:
            created = reference - timedelta(days=rng.randint(2, 25), hours=rng.randint(0, 23))
            last_activity = reference - timedelta(hours=rng.randint(2, 72))
        else:
            created = reference - timedelta(days=rng.randint(0, 25), hours=rng.randint(2, 23))
            last_activity = reference - timedelta(minutes=rng.randint(0, ABANDONMENT_MINUTES - 1))
        created = min(created, last_activity)
        session_duration = timedelta(minutes=rng.randint(5, 90))
        sessions.append({
            "session_id": session_id,
            "customer_id": customer_id,
            "device_type": rng.choice(["DESKTOP", "MOBILE", "TABLET"]),
            "started_at": max(created, last_activity - session_duration).isoformat(sep=" "),
            "ended_at": last_activity.isoformat(sep=" "),
        })

        cart_event_counter += 1
        cart_events.append({
            "event_id": cart_event_counter,
            "cart_id": cart_id,
            "event_type": "CREATED",
            "event_at": created.isoformat(sep=" "),
            "details": json.dumps({"source": "synthetic_checkout"}),
        })
        line_count = rng.randint(1, 4)
        total = 0
        for line_index in range(1, line_count + 1):
            sku, name, price = rng.choice(PRODUCTS)
            original_quantity = rng.randint(1, 3)
            quantity = original_quantity
            updated_at = last_activity - timedelta(minutes=rng.randint(0, 10))
            if rng.random() < 0.10:
                quantity += 1
                cart_event_counter += 1
                cart_events.append({
                    "event_id": cart_event_counter,
                    "cart_id": cart_id,
                    "event_type": "QUANTITY_UPDATED",
                    "event_at": updated_at.isoformat(sep=" "),
                    "details": json.dumps({"sku": sku, "from": original_quantity, "to": quantity}),
                })
            total += quantity * price
            line = {
                "cart_line_id": f"CL-{index:07d}-{line_index:02d}",
                "cart_id": cart_id,
                "sku": sku,
                "product_name": name,
                "quantity": quantity,
                "unit_price": price,
                "updated_at": updated_at.isoformat(sep=" "),
            }
            cart_lines.append(line)
            cart_line_index[cart_id].append(line)
        cart_event_counter += 1
        cart_events.append({
            "event_id": cart_event_counter,
            "cart_id": cart_id,
            "event_type": "ITEM_ADDED",
            "event_at": last_activity.isoformat(sep=" "),
            "details": json.dumps({"line_count": line_count}),
        })
        abandoned_at = last_activity + timedelta(minutes=ABANDONMENT_MINUTES) if is_abandoned_candidate else None
        if abandoned_at:
            cart_event_counter += 1
            cart_events.append({
                "event_id": cart_event_counter,
                "cart_id": cart_id,
                "event_type": "ABANDONED",
                "event_at": abandoned_at.isoformat(sep=" "),
                "details": json.dumps({"rule": "60_minute_inactivity"}),
            })
        carts.append({
            "cart_id": cart_id,
            "customer_id": customer_id,
            "session_id": session_id,
            "status": "ABANDONED" if is_abandoned_candidate else "ACTIVE",
            "currency": "INR",
            "cart_total": _money(total),
            "created_at": created.isoformat(sep=" "),
            "last_activity_at": last_activity.isoformat(sep=" "),
            "abandoned_at": abandoned_at.isoformat(sep=" ") if abandoned_at else "",
            "recovered_at": "",
            "closed_at": "",
        })

    # A campaign row represents a scheduled campaign execution instance.
    # Each execution is linked to one send attempt, while A/B/C encode the
    # reusable timing/channel variants.
    campaign_variant_by_delay = {
        1: ("EMAIL", "A"),
        6: ("SMS", "B"),
        24: ("EMAIL", "C"),
    }

    cart_by_id = {cart["cart_id"]: cart for cart in carts}
    cart_order = list(carts)
    orderable = rng.sample(cart_order, min(cart_count // 5, 5000))
    orders_by_cart = {}
    for index, cart in enumerate(orderable, 1):
        last_activity = _dt(cart["last_activity_at"])
        if cart["status"] == "ABANDONED":
            ordered_at = reference
            cart["status"] = "RECOVERED"
            cart["recovered_at"] = ordered_at.isoformat(sep=" ")
            cart_event_counter += 1
            cart_events.append({
                "event_id": cart_event_counter,
                "cart_id": cart["cart_id"],
                "event_type": "RECOVERED",
                "event_at": ordered_at.isoformat(sep=" "),
                "details": json.dumps({"source": "completed_order"}),
            })
        else:
            seconds_to_order = rng.randint(0, ABANDONMENT_MINUTES * 60 - 1)
            ordered_at = last_activity + timedelta(seconds=seconds_to_order)
            cart["status"] = "PURCHASED"
            cart_event_counter += 1
            cart_events.append({
                "event_id": cart_event_counter,
                "cart_id": cart["cart_id"],
                "event_type": "CLOSED",
                "event_at": ordered_at.isoformat(sep=" "),
                "details": json.dumps({"source": "completed_order_before_abandonment"}),
            })
        cart["closed_at"] = ordered_at.isoformat(sep=" ")
        total = sum(int(line["quantity"]) * float(line["unit_price"]) for line in cart_line_index[cart["cart_id"]])
        order_id = f"ORD-2026-{index:06d}"
        order = {
            "order_id": order_id,
            "customer_id": cart["customer_id"],
            "cart_id": cart["cart_id"],
            "order_status": "COMPLETED",
            "order_total": _money(total),
            "ordered_at": ordered_at.isoformat(sep=" "),
        }
        orders.append(order)
        orders_by_cart[cart["cart_id"]] = order
        for line_index, line in enumerate(cart_line_index[cart["cart_id"]], 1):
            order_lines.append({
                "order_line_id": f"OL-{index:06d}-{line_index:02d}",
                "order_id": order_id,
                "sku": line["sku"],
                "product_name": line["product_name"],
                "quantity": line["quantity"],
                "unit_price": line["unit_price"],
            })

    abandoned_carts = [cart for cart in carts if cart["abandoned_at"]]
    if send_count:
        candidates = [cart for cart in abandoned_carts if _dt(cart["abandoned_at"]) + timedelta(hours=1) <= reference]
        if send_count > len(candidates):
            raise ValueError("Not enough abandoned carts have reached the first campaign window")

        # Reserve four deterministic carts for a real, auditable 7-day cap case.
        # They share one opted-in customer and have 1h-variant send times 24h apart.
        cohort_size = min(4, send_count, len(candidates))
        cohort_carts = candidates[:cohort_size]
        selected_carts = cohort_carts + rng.sample(candidates[cohort_size:], send_count - cohort_size)
        if cohort_size == 4:
            cohort_customer = "CUS-000001"
            consent_index[(cohort_customer, "EMAIL")] = [{
                "consent_id": "CON-000001-EMAIL-01",
                "customer_id": cohort_customer,
                "channel": "EMAIL",
                "status": "OPTED_IN",
                "effective_at": (reference - timedelta(days=180)).isoformat(sep=" "),
                "withdrawn_at": "",
                "source": "PREFERENCE_CENTER",
            }]
            consents[:] = [row for row in consents if not (row["customer_id"] == cohort_customer and row["channel"] == "EMAIL")]
            consents.extend(consent_index[(cohort_customer, "EMAIL")])
            session_by_id = {row["session_id"]: row for row in sessions}
            target_attempts = [reference - timedelta(hours=72), reference - timedelta(hours=48), reference - timedelta(hours=24), reference - timedelta(hours=1)]
            for cohort_index, (cart, target_attempt) in enumerate(zip(cohort_carts, target_attempts)):
                cart["customer_id"] = cohort_customer
                session = session_by_id[cart["session_id"]]
                session["customer_id"] = cohort_customer
                session["device_type"] = ["DESKTOP", "MOBILE", "TABLET", "DESKTOP"][cohort_index]
                last_activity = target_attempt - timedelta(hours=2)
                abandoned_at = target_attempt - timedelta(hours=1)
                cart["created_at"] = (last_activity - timedelta(hours=1)).isoformat(sep=" ")
                cart["last_activity_at"] = last_activity.isoformat(sep=" ")
                cart["abandoned_at"] = abandoned_at.isoformat(sep=" ")
                session["started_at"] = (last_activity - timedelta(hours=1, minutes=30)).isoformat(sep=" ")
                session["ended_at"] = last_activity.isoformat(sep=" ")
                if cart["cart_id"] in orders_by_cart:
                    orders_by_cart[cart["cart_id"]]["customer_id"] = cohort_customer
                for line in cart_line_index[cart["cart_id"]]:
                    line["updated_at"] = (last_activity - timedelta(minutes=5)).isoformat(sep=" ")
                for event in cart_events:
                    if event["cart_id"] == cart["cart_id"]:
                        if event["event_type"] == "CREATED":
                            event["event_at"] = cart["created_at"]
                        elif event["event_type"] in ("ITEM_ADDED", "ABANDONED"):
                            event["event_at"] = last_activity.isoformat(sep=" ") if event["event_type"] == "ITEM_ADDED" else abandoned_at.isoformat(sep=" ")
                        elif event["event_type"] == "QUANTITY_UPDATED":
                            event["event_at"] = (last_activity - timedelta(minutes=5)).isoformat(sep=" ")
    else:
        selected_carts = []
    pending_attempts = []
    for index, cart in enumerate(selected_carts, 1):
        due_delays = [delay for delay in CAMPAIGN_DELAYS if _dt(cart["abandoned_at"]) + timedelta(hours=delay) <= reference]
        delay = 1 if index <= 4 and len(selected_carts) >= 4 else rng.choice(due_delays)
        channel, variant = campaign_variant_by_delay[delay]
        campaign_id = f"CMP-2026-{index:06d}"
        template_id = f"TPL-{index:06d}"
        attempted_at = _dt(cart["abandoned_at"]) + timedelta(hours=delay)
        campaign = {
            "campaign_id": campaign_id,
            "campaign_name": f"{delay}-hour Recovery {channel} {variant}",
            "channel": channel,
            "variant": variant,
            "target_audience": "ABANDONED_CARTS",
            "scheduled_at": attempted_at.isoformat(sep=" "),
            "status": "COMPLETED",
            "created_at": (attempted_at - timedelta(days=1)).isoformat(sep=" "),
        }
        template = {
            "template_id": template_id,
            "campaign_id": campaign_id,
            "channel": channel,
            "subject": "Your cart is waiting" if channel == "EMAIL" else "",
            "body": "Hi {{customer_name}}, your cart {{cart_id}} worth {{cart_value}} is waiting. Continue: {{recovery_link}}",
        }
        campaigns.append(campaign)
        templates.append(template)
        pending_attempts.append({
            "index": index,
            "cart": cart,
            "campaign": campaign,
            "template": template,
            "channel": channel,
            "attempted_at": attempted_at,
        })
    pending_attempts.sort(key=lambda item: (item["attempted_at"], item["index"]))
    sent_times = defaultdict(list)
    sent_carts = set()
    send_events_by_send = defaultdict(list)
    send_event_counter = 0
    audit_counter = 0
    truth_by_cart = {
        cart["cart_id"]: {
            "cart_id": cart["cart_id"],
            "expected_abandoned_status": cart["status"],
            "expected_consent_eligible": "",
            "expected_suppression_decision": "",
            "expected_campaign_eligible": "",
            "expected_attribution": "",
            "expected_anomaly_classification": "NONE",
            "expected_revenue_attribution": "0.00",
        }
        for cart in carts
    }

    for attempt in pending_attempts:
        index, cart = attempt["index"], attempt["cart"]
        channel, attempted_at = attempt["channel"], attempt["attempted_at"]
        customer_id = cart["customer_id"]
        latest = _latest_consent(consent_index, customer_id, channel, attempted_at)
        reason = None
        if latest is None or latest["status"] != "OPTED_IN":
            reason = f"CONSENT_{latest['status'] if latest else 'UNKNOWN'}"
        order = orders_by_cart.get(cart["cart_id"])
        if reason is None and order and _dt(order["ordered_at"]) <= attempted_at:
            reason = "ALREADY_PURCHASED"
        recent = [sent for sent in sent_times[(customer_id, channel)] if sent >= attempted_at - timedelta(days=7)]
        if reason is None and len(recent) >= 3:
            reason = "FREQUENCY_CAP_7D"
        if reason is None and recent and attempted_at - max(recent) < timedelta(hours=24):
            reason = "MIN_INTERVAL_24H"
        if reason is None and cart["cart_id"] in sent_carts:
            reason = "DUPLICATE_CART_RECOVERY"

        send_id = f"SEND-2026-{index:06d}"
        status = "SUPPRESSED" if reason else "DELIVERED"
        event_at = ""
        if reason is None:
            sent_times[(customer_id, channel)].append(attempted_at)
            sent_carts.add(cart["cart_id"])
            send_event_counter += 1
            send_events.append({"event_id": send_event_counter, "send_id": send_id, "event_type": "SENT", "event_at": attempted_at.isoformat(sep=" ")})
            event_time = attempted_at + timedelta(minutes=rng.randint(1, 5))
            if event_time > reference:
                event_time = reference
            if rng.random() < 0.05:
                status = "BOUNCED"
                event_type = "BOUNCED"
            else:
                status = "DELIVERED"
                event_type = "DELIVERED"
            send_event_counter += 1
            send_events.append({"event_id": send_event_counter, "send_id": send_id, "event_type": event_type, "event_at": event_time.isoformat(sep=" ")})
            event_at = event_time.isoformat(sep=" ")
            if status == "DELIVERED" and rng.random() < 0.45:
                open_time = min(reference, event_time + timedelta(minutes=rng.randint(1, 120)))
                send_event_counter += 1
                send_events.append({"event_id": send_event_counter, "send_id": send_id, "event_type": "OPENED", "event_at": open_time.isoformat(sep=" ")})
                event_at = open_time.isoformat(sep=" ")
                status = "OPENED"
                if rng.random() < 0.30:
                    click_time = min(reference, open_time + timedelta(minutes=rng.randint(1, 60)))
                    send_event_counter += 1
                    send_events.append({"event_id": send_event_counter, "send_id": send_id, "event_type": "CLICKED", "event_at": click_time.isoformat(sep=" ")})
                    event_at = click_time.isoformat(sep=" ")
                    status = "CLICKED"
            send_events_by_send[send_id] = [event for event in send_events if event["send_id"] == send_id]
        sends.append({
            "send_id": send_id,
            "campaign_id": attempt["campaign"]["campaign_id"],
            "template_id": attempt["template"]["template_id"],
            "customer_id": customer_id,
            "cart_id": cart["cart_id"],
            "channel": channel,
            "status": status,
            "attempted_at": attempted_at.isoformat(sep=" "),
            "event_at": event_at,
            "failure_reason": reason or "",
            "recovery_link": f"https://shop.example.test/recover/{cart['cart_id']}",
        })
        audit_counter += 1
        audit_decisions.append({
            "decision_id": audit_counter,
            "customer_id": customer_id,
            "cart_id": cart["cart_id"],
            "channel": channel,
            "decision": "SUPPRESSED" if reason else "ELIGIBLE",
            "reason_code": reason or "ELIGIBLE",
            "detail": f"Campaign {attempt['campaign']['campaign_id']} at {attempted_at.isoformat(sep=' ')}",
            "decided_at": attempted_at.isoformat(sep=" "),
        })
        truth = truth_by_cart[cart["cart_id"]]
        truth["expected_consent_eligible"] = "YES" if latest and latest["status"] == "OPTED_IN" else "NO"
        truth["expected_suppression_decision"] = "SUPPRESS" if reason else "ALLOW"
        truth["expected_campaign_eligible"] = "NO" if reason else "YES"

    send_by_id = {send["send_id"]: send for send in sends}
    events_by_send = defaultdict(list)
    for event in send_events:
        events_by_send[event["send_id"]].append(event)
    order_by_id = {order["order_id"]: order for order in orders}
    attribution_counter = 0
    for order in orders:
        order_at = _dt(order["ordered_at"])
        qualifying = []
        for send in sends:
            if send["customer_id"] != order["customer_id"] or send["cart_id"] != order["cart_id"]:
                continue
            if send["status"] in ("SUPPRESSED", "BOUNCED"):
                continue
            for event in events_by_send[send["send_id"]]:
                event_at = _dt(event["event_at"])
                if (
                    event["event_type"] in ("DELIVERED", "OPENED", "CLICKED")
                    and _dt(send["attempted_at"]) <= event_at <= order_at
                    and order_at - event_at <= timedelta(days=ATTRIBUTION_DAYS)
                ):
                    priority = {"DELIVERED": 1, "OPENED": 2, "CLICKED": 3}[event["event_type"]]
                    qualifying.append((priority, event_at, send["send_id"], send))
        if not qualifying:
            continue
        _, interaction_at, send_id, send = max(qualifying, key=lambda item: (item[0], item[1], item[2]))
        attribution_counter += 1
        attributions.append({
            "attribution_id": attribution_counter,
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "cart_id": order["cart_id"],
            "campaign_id": send["campaign_id"],
            "send_id": send_id,
            "model": "LAST_TOUCH_7D",
            "attributed_at": interaction_at.isoformat(sep=" "),
            "attributed_revenue": order["order_total"],
            "reason": f"Last qualifying {next(event['event_type'] for event in events_by_send[send_id] if event['event_at'] == interaction_at.isoformat(sep=' '))} within {ATTRIBUTION_DAYS} days",
        })
        truth_by_cart[order["cart_id"]]["expected_attribution"] = send["campaign_id"]
        truth_by_cart[order["cart_id"]]["expected_revenue_attribution"] = order["order_total"]

    ground_truth = list(truth_by_cart.values())
    cart_events.sort(key=lambda row: (row["event_at"], row["event_id"]))
    send_events.sort(key=lambda row: (row["event_at"], row["event_id"]))
    anomalies = [
        {
            "issue_type": "MESSAGE_AFTER_OPTOUT",
            "ground_truth": "CONSENT_WITHDRAWN",
            "expected_decision": "BLOCK_SEND",
            "actual_decision": "SEND_RECORDED",
            "affected_entity_id": consents[-1]["customer_id"],
            "description": "Isolated negative fixture; not a baseline send. A contact attempt after the final opt-out must be blocked.",
            "detected_at": REFERENCE_TIME,
        },
        {
            "issue_type": "CART_ABANDONED_AFTER_PURCHASE",
            "ground_truth": "ORDER_PRECEDES_EVALUATION",
            "expected_decision": "NOT_ABANDONED",
            "actual_decision": "ABANDONED",
            "affected_entity_id": orderable[0]["cart_id"] if orderable else carts[0]["cart_id"],
            "description": "Isolated negative fixture; a qualifying purchase before evaluation prevents abandonment.",
            "detected_at": REFERENCE_TIME,
        },
        {
            "issue_type": "ATTRIBUTION_DOUBLE_COUNT",
            "ground_truth": "ONE_ORDER_ONE_CREDIT",
            "expected_decision": "FLAG_DUPLICATE",
            "actual_decision": "MULTIPLE_CAMPAIGNS_CREDITED",
            "affected_entity_id": orders[0]["order_id"] if orders else "ORD-2026-000001",
            "description": "Isolated negative fixture; one order must not receive credit from multiple campaigns.",
            "detected_at": REFERENCE_TIME,
        },
        {
            "issue_type": "STALE_CART_TOTAL",
            "ground_truth": "LINE_SUM_IS_SOURCE_OF_TRUTH",
            "expected_decision": "RECALCULATE_TOTAL",
            "actual_decision": "STALE_TOTAL_RETAINED",
            "affected_entity_id": carts[-1]["cart_id"],
            "description": "Isolated negative fixture; totals are reconciled from final quantities in baseline records.",
            "detected_at": REFERENCE_TIME,
        },
    ]

    tables = {
        "customers": customers,
        "consents": consents,
        "sessions": sessions,
        "carts": carts,
        "cart_lines": cart_lines,
        "campaigns": campaigns,
        "message_templates": templates,
        "send_attempts": sends,
        "send_events": send_events,
        "orders": orders,
        "order_lines": order_lines,
        "attributions": attributions,
        "audit_decisions": audit_decisions,
        "cart_events": cart_events,
        "ground_truth": ground_truth,
        "anomalies": anomalies,
    }
    for name, rows in tables.items():
        _write_table(output, name, rows)

    _write_sql_seed(output, tables)
    source_manifest = {
        "provenance": "fully synthetic; no external or personal datasets used",
        "generator": "generator/generate_data.py",
        "seed": SEED,
        "reference_time": REFERENCE_TIME,
        "profile": profile,
        "external_sources": [],
        "license_note": "Synthetic records generated for this project; no third-party dataset license applies.",
    }
    (output / "source_manifest.json").write_text(json.dumps(source_manifest, indent=2), encoding="utf-8")

    delivered_events = sum(event["event_type"] == "DELIVERED" for event in send_events)
    opened_events = sum(event["event_type"] == "OPENED" for event in send_events)
    clicked_events = sum(event["event_type"] == "CLICKED" for event in send_events)
    suppressed_attempts = sum(send["status"] == "SUPPRESSED" for send in sends)
    recovered_carts = sum(cart["status"] == "RECOVERED" for cart in carts)
    total_order_revenue = sum(float(order["order_total"]) for order in orders)
    attributed_revenue = sum(float(row["attributed_revenue"]) for row in attributions)
    report = {
        "profile": profile,
        "seed": SEED,
        "reference_time": REFERENCE_TIME,
        "abandonment_window_minutes": ABANDONMENT_MINUTES,
        "attribution_window_days": ATTRIBUTION_DAYS,
        "frequency_cap_per_channel_7d": 3,
        "minimum_hours_between_sends": 24,
        "row_counts": {name: len(rows) for name, rows in tables.items()},
        "abandonment_candidates": abandoned_target,
        "recovered_carts": recovered_carts,
        "attributed_orders": len(attributions),
        "metrics": {
            "abandonment_rate": round(abandoned_target / cart_count, 4),
            "recovery_rate_of_abandoned_carts": round(recovered_carts / abandoned_target, 4) if abandoned_target else 0.0,
            "suppression_rate_of_attempts": round(suppressed_attempts / len(sends), 4) if sends else 0.0,
            "delivery_rate_of_attempts": round(delivered_events / len(sends), 4) if sends else 0.0,
            "open_rate_of_delivered": round(opened_events / delivered_events, 4) if delivered_events else 0.0,
            "click_rate_of_opened": round(clicked_events / opened_events, 4) if opened_events else 0.0,
            "attributed_conversion_rate_of_delivered": round(len(attributions) / delivered_events, 4) if delivered_events else 0.0,
            "total_order_revenue_inr": round(total_order_revenue, 2),
            "attributed_revenue_inr": round(attributed_revenue, 2),
            "attributed_revenue_share": round(attributed_revenue / total_order_revenue, 4) if total_order_revenue else 0.0,
        },
    }
    (output / "generation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    checksums = {}
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "reproducibility_sha256.json":
            checksums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "reproducibility_sha256.json").write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=PROFILES, default="starter")
    parser.add_argument("--output", default="data/starter")
    args = parser.parse_args()
    generate(args.profile, args.output)
