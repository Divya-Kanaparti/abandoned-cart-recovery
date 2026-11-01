import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

PRIMARY_KEYS = {
    "customers": "customer_id",
    "consents": "consent_id",
    "sessions": "session_id",
    "carts": "cart_id",
    "cart_lines": "cart_line_id",
    "campaigns": "campaign_id",
    "message_templates": "template_id",
    "send_attempts": "send_id",
    "send_events": "event_id",
    "orders": "order_id",
    "order_lines": "order_line_id",
    "attributions": "attribution_id",
    "audit_decisions": "decision_id",
    "cart_events": "event_id",
    "ground_truth": "cart_id",
}
FOREIGN_KEYS = {
    "consents": {"customer_id": "customers"},
    "sessions": {"customer_id": "customers"},
    "carts": {"customer_id": "customers", "session_id": "sessions"},
    "cart_lines": {"cart_id": "carts"},
    "message_templates": {"campaign_id": "campaigns"},
    "send_attempts": {
        "campaign_id": "campaigns",
        "template_id": "message_templates",
        "customer_id": "customers",
        "cart_id": "carts",
    },
    "send_events": {"send_id": "send_attempts"},
    "orders": {"customer_id": "customers", "cart_id": "carts"},
    "order_lines": {"order_id": "orders"},
    "attributions": {
        "order_id": "orders",
        "customer_id": "customers",
        "cart_id": "carts",
        "campaign_id": "campaigns",
        "send_id": "send_attempts",
    },
    "audit_decisions": {"customer_id": "customers", "cart_id": "carts"},
    "cart_events": {"cart_id": "carts"},
}
ENUMS = {
    ("consents", "channel"): {"EMAIL", "SMS"},
    ("consents", "status"): {"OPTED_IN", "OPTED_OUT", "UNKNOWN"},
    ("sessions", "device_type"): {"DESKTOP", "MOBILE", "TABLET"},
    ("carts", "status"): {"ACTIVE", "ABANDONED", "RECOVERY_PENDING", "RECOVERED", "EXPIRED", "SUPPRESSED", "PURCHASED"},
    ("campaigns", "channel"): {"EMAIL", "SMS"},
    ("campaigns", "variant"): {"A", "B", "C"},
    ("campaigns", "status"): {"DRAFT", "SCHEDULED", "RUNNING", "COMPLETED", "CANCELLED"},
    ("message_templates", "channel"): {"EMAIL", "SMS"},
    ("send_attempts", "channel"): {"EMAIL", "SMS"},
    ("send_attempts", "status"): {"SEND_ATTEMPTED", "SENT", "DELIVERED", "BOUNCED", "OPENED", "CLICKED", "FAILED", "SUPPRESSED"},
    ("orders", "order_status"): {"COMPLETED", "CANCELLED", "REFUNDED"},
    ("attributions", "model"): {"LAST_TOUCH_7D"},
    ("audit_decisions", "decision"): {"ELIGIBLE", "SUPPRESSED", "BLOCKED"},
    ("cart_events", "event_type"): {"CREATED", "ITEM_ADDED", "QUANTITY_UPDATED", "ITEM_REMOVED", "ABANDONED", "RECOVERED", "CLOSED"},
    ("send_events", "event_type"): {"SENT", "DELIVERED", "BOUNCED", "OPENED", "CLICKED"},
}
DATE_FIELDS = {
    "customers": ("created_at",),
    "consents": ("effective_at", "withdrawn_at"),
    "sessions": ("started_at", "ended_at"),
    "carts": ("created_at", "last_activity_at", "abandoned_at", "recovered_at", "closed_at"),
    "cart_lines": ("updated_at",),
    "campaigns": ("scheduled_at", "created_at"),
    "send_attempts": ("attempted_at", "event_at"),
    "send_events": ("event_at",),
    "orders": ("ordered_at",),
    "attributions": ("attributed_at",),
    "audit_decisions": ("decided_at",),
    "cart_events": ("event_at",),
}


def _read(folder, name):
    path = folder / f"{name}.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _date(value):
    return datetime.fromisoformat(value) if value else None


def _issue(issues, table, row_key, code, detail=""):
    issues.append({"file": f"{table}.csv", "row_key": row_key, "issue": code, "detail": detail})


def validate(folder, output):
    folder, output = Path(folder), Path(output)
    if not folder.is_dir():
        raise FileNotFoundError(f"Input data directory does not exist: {folder}")
    output.mkdir(parents=True, exist_ok=True)
    table_names = [path.stem for path in folder.glob("*.csv") if path.stem not in ("anomalies",)]
    tables = {name: _read(folder, name) for name in table_names}
    issues = []
    counts = {name: len(rows) for name, rows in sorted(tables.items())}

    for table, key in PRIMARY_KEYS.items():
        rows = tables.get(table, [])
        seen = set()
        for index, row in enumerate(rows, 2):
            value = row.get(key, "")
            if not value:
                _issue(issues, table, index, "MISSING_PRIMARY_KEY", key)
            elif value in seen:
                _issue(issues, table, index, "DUPLICATE_PRIMARY_KEY", value)
            seen.add(value)

    for table, relations in FOREIGN_KEYS.items():
        rows = tables.get(table, [])
        for field, parent in relations.items():
            parent_rows = tables.get(parent, [])
            parent_key = PRIMARY_KEYS[parent]
            valid_ids = {row.get(parent_key) for row in parent_rows}
            for index, row in enumerate(rows, 2):
                if row.get(field) not in valid_ids:
                    _issue(issues, table, index, "FOREIGN_KEY_NOT_FOUND", f"{field}={row.get(field)}")

    for (table, field), allowed in ENUMS.items():
        for index, row in enumerate(tables.get(table, []), 2):
            if row.get(field) not in allowed:
                _issue(issues, table, index, "INVALID_ENUM", f"{field}={row.get(field)}")

    parsed_dates = {}
    for table, fields in DATE_FIELDS.items():
        for index, row in enumerate(tables.get(table, []), 2):
            for field in fields:
                try:
                    parsed_dates[(table, row.get(PRIMARY_KEYS.get(table, ""), str(index)), field)] = _date(row.get(field, ""))
                except ValueError:
                    _issue(issues, table, index, "INVALID_DATETIME", f"{field}={row.get(field)}")

    customers = {row["customer_id"]: row for row in tables.get("customers", [])}
    sessions = {row["session_id"]: row for row in tables.get("sessions", [])}
    carts = {row["cart_id"]: row for row in tables.get("carts", [])}
    orders = {row["order_id"]: row for row in tables.get("orders", [])}
    sends = {row["send_id"]: row for row in tables.get("send_attempts", [])}
    campaigns = {row["campaign_id"]: row for row in tables.get("campaigns", [])}
    templates = {row["template_id"]: row for row in tables.get("message_templates", [])}

    for cart in carts.values():
        cart_id = cart["cart_id"]
        created, activity = _date(cart["created_at"]), _date(cart["last_activity_at"])
        if created and activity and created > activity:
            _issue(issues, "carts", cart_id, "CREATED_AFTER_LAST_ACTIVITY")
        cart_session = sessions.get(cart["session_id"])
        if cart_session and cart_session["customer_id"] != cart["customer_id"]:
            _issue(issues, "carts", cart_id, "SESSION_CUSTOMER_MISMATCH")
        if created and activity:
            inactive = datetime.fromisoformat("2026-10-30T12:00:00") - activity
            if cart["status"] == "ACTIVE" and inactive >= timedelta(minutes=60):
                _issue(issues, "carts", cart_id, "ACTIVE_CART_PAST_ABANDONMENT_WINDOW")
        if cart["status"] in ("ABANDONED", "RECOVERED") and not cart.get("abandoned_at"):
            _issue(issues, "carts", cart_id, "MISSING_ABANDONED_AT")
        if cart["status"] == "RECOVERED" and not cart.get("recovered_at"):
            _issue(issues, "carts", cart_id, "MISSING_RECOVERED_AT")
        abandoned_at = _date(cart.get("abandoned_at", ""))
        if abandoned_at and activity and abandoned_at != activity + timedelta(minutes=60):
            _issue(issues, "carts", cart_id, "ABANDONMENT_TIMESTAMP_MISMATCH")
        recovered_at = _date(cart.get("recovered_at", ""))
        if recovered_at and created and recovered_at < created:
            _issue(issues, "carts", cart_id, "RECOVERY_BEFORE_CART_CREATION")

    for session in sessions.values():
        started, ended = _date(session["started_at"]), _date(session.get("ended_at", ""))
        if started and ended and ended < started:
            _issue(issues, "sessions", session["session_id"], "SESSION_END_BEFORE_START")

    for consent in tables.get("consents", []):
        effective = _date(consent.get("effective_at", ""))
        withdrawn = _date(consent.get("withdrawn_at", ""))
        if withdrawn and effective and withdrawn < effective:
            _issue(issues, "consents", consent.get("consent_id", ""), "WITHDRAWAL_BEFORE_EFFECTIVE_DATE")
        if withdrawn and consent.get("status") != "OPTED_OUT":
            _issue(issues, "consents", consent.get("consent_id", ""), "WITHDRAWAL_STATUS_MISMATCH")

    cart_event_groups = defaultdict(list)
    for event in tables.get("cart_events", []):
        cart_event_groups[event["cart_id"]].append(_date(event["event_at"]))
    for cart_id, event_times in cart_event_groups.items():
        if event_times != sorted(event_times):
            _issue(issues, "cart_events", cart_id, "CART_EVENTS_NOT_CHRONOLOGICAL")

    cart_totals = defaultdict(float)
    for line in tables.get("cart_lines", []):
        try:
            quantity, price = int(line["quantity"]), float(line["unit_price"])
            if quantity <= 0 or price < 0:
                _issue(issues, "cart_lines", line["cart_line_id"], "INVALID_LINE_AMOUNT")
            cart_totals[line["cart_id"]] += quantity * price
        except (KeyError, ValueError):
            _issue(issues, "cart_lines", line.get("cart_line_id", ""), "INVALID_LINE_AMOUNT")
    for cart_id, cart in carts.items():
        if abs(float(cart["cart_total"]) - cart_totals[cart_id]) > 0.01:
            _issue(issues, "carts", cart_id, "CART_TOTAL_MISMATCH")

    order_totals = defaultdict(float)
    for line in tables.get("order_lines", []):
        try:
            order_totals[line["order_id"]] += int(line["quantity"]) * float(line["unit_price"])
        except (KeyError, ValueError):
            _issue(issues, "order_lines", line.get("order_line_id", ""), "INVALID_LINE_AMOUNT")
    for order in orders.values():
        if abs(float(order["order_total"]) - order_totals[order["order_id"]]) > 0.01:
            _issue(issues, "orders", order["order_id"], "ORDER_TOTAL_MISMATCH")
        cart = carts.get(order["cart_id"])
        if cart and cart["customer_id"] != order["customer_id"]:
            _issue(issues, "orders", order["order_id"], "ORDER_CUSTOMER_MISMATCH")
        if cart and _date(order["ordered_at"]) < _date(cart["created_at"]):
            _issue(issues, "orders", order["order_id"], "ORDER_BEFORE_CART_CREATION")

    consent_index = defaultdict(list)
    for consent in tables.get("consents", []):
        consent_index[(consent["customer_id"], consent["channel"])].append(consent)

    # Validate consent, purchase timing, duplicate cart-campaign sends,
    # and frequency caps for each customer across EMAIL and SMS.
    attempts_by_customer = defaultdict(list)
    sent_cart_campaigns = set()

    for send in sends.values():
        send_id = send["send_id"]
        campaign = campaigns.get(send["campaign_id"])
        template = templates.get(send["template_id"])

        if campaign and campaign["channel"] != send["channel"]:
            _issue(issues, "send_attempts", send_id, "CAMPAIGN_CHANNEL_MISMATCH")
        if template and template["channel"] != send["channel"]:
            _issue(issues, "send_attempts", send_id, "TEMPLATE_CHANNEL_MISMATCH")

        at = _date(send["attempted_at"])
        latest = max(
            (
                row for row in consent_index[(send["customer_id"], send["channel"])]
                if _date(row["effective_at"]) <= at
            ),
            key=lambda row: row["effective_at"],
            default=None,
        )

        if send["status"] != "SUPPRESSED" and (
            latest is None or latest["status"] != "OPTED_IN"
        ):
            _issue(issues, "send_attempts", send_id, "SEND_WITHOUT_EFFECTIVE_OPT_IN")

        if send["status"] != "SUPPRESSED":
            order = next(
                (row for row in orders.values() if row["cart_id"] == send["cart_id"]),
                None,
            )
            if order and _date(order["ordered_at"]) <= at:
                _issue(issues, "send_attempts", send_id, "SEND_AFTER_PURCHASE")

            attempts_by_customer[send["customer_id"]].append((at, send_id))

            cart_campaign_key = (send["cart_id"], send["campaign_id"])
            if cart_campaign_key in sent_cart_campaigns:
                _issue(issues, "send_attempts", send_id, "DUPLICATE_CART_SEND")
            sent_cart_campaigns.add(cart_campaign_key)

    # Enforce the documented policy independently per channel:
    # maximum 3 non-suppressed attempts in a rolling 7-day window and
    # at least 24 hours between attempts for the same customer/channel.
    sends_by_customer_channel = defaultdict(list)
    for send in sends.values():
        if send["status"] != "SUPPRESSED":
            sends_by_customer_channel[(send["customer_id"], send["channel"])].append(
                (_date(send["attempted_at"]), send["send_id"])
            )
    for _, attempt_rows in sends_by_customer_channel.items():
        attempt_rows.sort()
        for index, (at, send_id) in enumerate(attempt_rows):
            previous = attempt_rows[:index]
            recent_7d = [row for row in previous if row[0] > at - timedelta(days=7)]
            if len(recent_7d) >= 3:
                _issue(issues, "send_attempts", send_id, "FREQUENCY_CAP_7D_EXCEEDED")
            if previous and at - previous[-1][0] < timedelta(hours=24):
                _issue(issues, "send_attempts", send_id, "MINIMUM_SEND_INTERVAL_VIOLATION")

    events_by_send = defaultdict(list)
    for event in tables.get("send_events", []):
        events_by_send[event["send_id"]].append(event)
    for send_id, event_rows in events_by_send.items():
        event_times = [_date(row["event_at"]) for row in event_rows]
        if event_times != sorted(event_times):
            _issue(issues, "send_events", send_id, "EVENTS_NOT_CHRONOLOGICAL")
        send = sends.get(send_id)
        if send and any(event_at < _date(send["attempted_at"]) for event_at in event_times):
            _issue(issues, "send_events", send_id, "EVENT_BEFORE_SEND")

    for send_id, event_rows in events_by_send.items():
        sequence = [row["event_type"] for row in event_rows]
        if sequence and sequence[0] != "SENT":
            _issue(issues, "send_events", send_id, "SEND_EVENT_SEQUENCE_MISSING_SENT")
        if "BOUNCED" in sequence and any(event in sequence for event in ("DELIVERED", "OPENED", "CLICKED")):
            _issue(issues, "send_events", send_id, "BOUNCE_AFTER_DELIVERY_EVENT")
        if "CLICKED" in sequence and "OPENED" not in sequence:
            _issue(issues, "send_events", send_id, "CLICK_WITHOUT_OPEN")
        if "OPENED" in sequence and "DELIVERED" not in sequence:
            _issue(issues, "send_events", send_id, "OPEN_WITHOUT_DELIVERY")

    attributions_by_order = defaultdict(list)
    for attribution in tables.get("attributions", []):
        attributions_by_order[attribution["order_id"]].append(attribution)
        order = orders.get(attribution["order_id"])
        send = sends.get(attribution["send_id"])
        if order and send and (
            attribution["customer_id"] != order["customer_id"]
            or attribution["cart_id"] != order["cart_id"]
            or send["customer_id"] != order["customer_id"]
            or send["cart_id"] != order["cart_id"]
            or attribution["campaign_id"] != send["campaign_id"]
        ):
            _issue(issues, "attributions", attribution["attribution_id"], "ATTRIBUTION_RELATIONSHIP_MISMATCH")
        if order and abs(float(attribution["attributed_revenue"]) - float(order["order_total"])) > 0.01:
            _issue(issues, "attributions", attribution["attribution_id"], "ATTRIBUTED_REVENUE_MISMATCH")
        if order and _date(attribution["attributed_at"]) > _date(order["ordered_at"]):
            _issue(issues, "attributions", attribution["attribution_id"], "ATTRIBUTION_AFTER_ORDER")
        if order and _date(order["ordered_at"]) - _date(attribution["attributed_at"]) > timedelta(days=7):
            _issue(issues, "attributions", attribution["attribution_id"], "ATTRIBUTION_OUTSIDE_WINDOW")
        if send and send["status"] in ("SUPPRESSED", "BOUNCED"):
            _issue(issues, "attributions", attribution["attribution_id"], "ATTRIBUTION_FROM_UNQUALIFIED_SEND")
    for order_id, attribution_rows in attributions_by_order.items():
        if len(attribution_rows) > 1:
            _issue(issues, "attributions", order_id, "DUPLICATE_ORDER_ATTRIBUTION")

    expected_counts = {}
    for row in _read(folder, "ground_truth"):
        expected_counts[row["cart_id"]] = row
    for cart_id, row in expected_counts.items():
        if cart_id not in carts:
            _issue(issues, "ground_truth", cart_id, "GROUND_TRUTH_CART_NOT_FOUND")

    report_path = folder / "generation_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        expected_cart_count = report.get("row_counts", {}).get("carts")
        if expected_cart_count is not None and expected_cart_count != len(carts):
            _issue(issues, "generation_report", "carts", "REPORT_CART_COUNT_MISMATCH")
        expected_abandoned = report.get("abandonment_candidates")
        actual_abandoned = sum(bool(row.get("abandoned_at")) for row in carts.values())
        if expected_abandoned is not None and expected_abandoned != actual_abandoned:
            _issue(issues, "generation_report", "abandoned_at", "REPORT_ABANDONMENT_COUNT_MISMATCH")

    anomaly_rows = _read(folder, "anomalies")
    expected_anomalies = {
        "MESSAGE_AFTER_OPTOUT", "CART_ABANDONED_AFTER_PURCHASE",
        "ATTRIBUTION_DOUBLE_COUNT", "STALE_CART_TOTAL",
    }
    actual_anomalies = {row.get("issue_type") for row in anomaly_rows}
    for missing in sorted(expected_anomalies - actual_anomalies):
        _issue(issues, "anomalies", missing, "REQUIRED_ANOMALY_FIXTURE_MISSING")
    summary = {
        "status": "FAIL" if issues else ("PASS_WITH_LABELLED_ANOMALIES" if anomaly_rows else "PASS"),
        "row_counts": counts,
        "validation_issue_count": len(issues),
        "labelled_anomaly_count": len(anomaly_rows),
        "issues": issues,
    }
    (output / "validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (output / "validation_issues.csv").open("w", newline="", encoding="utf-8") as file:
        fieldnames = ["file", "row_key", "issue", "detail"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/starter")
    parser.add_argument("--output", default="data/starter/validation")
    args = parser.parse_args()
    validate(args.input, args.output)
