from datetime import timedelta

def is_abandoned(cart, now, abandonment_minutes=60, has_purchase=False):
    if has_purchase or not cart.get("has_items", True): return False
    if cart.get("status") in {"RECOVERED","EXPIRED","SUPPRESSED"}: return False
    return now-cart["last_activity_at"] >= timedelta(minutes=abandonment_minutes)

# def latest_consent(records, channel, at):
#     eligible=[r for r in records if r["channel"]==channel and r["effective_at"]<=at]
#     if not eligible: return "UNKNOWN"
#     return sorted(eligible,key=lambda r:r["effective_at"])[-1]["status"]


def latest_consent(records, channel, at):
    # Consider only consent records effective at the given time
    eligible = [
        r for r in records
        if r["channel"] == channel
        and r["effective_at"] <= at
    ]

    # No consent record means consent is unknown
    if not eligible:
        return "UNKNOWN"

    # Select the most recent consent record
    latest = max(
        eligible,
        key=lambda r: (
            r["effective_at"],
            r.get("consent_id", 0) or 0
        )
    )

    status = latest["status"]

    # A withdrawal overrides an earlier opt-in
    withdrawn_at = latest.get("withdrawn_at")

    if (
        status == "OPTED_IN"
        and withdrawn_at is not None
        and withdrawn_at <= at
    ):
        return "OPTED_OUT"

    return status

def suppression_reason(customer, cart, channel, consents, sends, now, max_7d=3, min_hours=24, purchased=False):
    status=latest_consent(consents,channel,now)
    if status!="OPTED_IN": return "CONSENT_"+status
    if purchased: return "ALREADY_PURCHASED"
    if cart.get("status") not in {"ABANDONED","RECOVERY_PENDING"}: return "CART_NOT_ELIGIBLE"
    recent=[
        s for s in sends
        if s["customer_id"] == customer
        and s.get("channel", channel) == channel
        and s.get("status") not in {"FAILED", "SUPPRESSED"}
        and s["attempted_at"] >= now - timedelta(days=7)
    ]
    if len(recent)>=max_7d: return "FREQUENCY_CAP_7D"
    if recent and now-max(s["attempted_at"] for s in recent)<timedelta(hours=min_hours): return "MIN_INTERVAL"
    if any(s["cart_id"]==cart["cart_id"] and s["status"] not in {"FAILED","SUPPRESSED"} for s in sends): return "DUPLICATE_CART_RECOVERY"
    return None

def choose_attribution(order, interactions, window_days=7):
    eligible=[x for x in interactions if x["customer_id"]==order["customer_id"] and x["cart_id"]==order["cart_id"] and x["interaction_at"]<=order["ordered_at"] and order["ordered_at"]-x["interaction_at"]<=timedelta(days=window_days)]
    if not eligible: return None
    # Last qualifying click wins; if no click, last open; otherwise last delivery.
    priority={"CLICKED":3,"OPENED":2,"DELIVERED":1}
    eligible.sort(key=lambda x:(priority.get(x["event"],0),x["interaction_at"],x["send_id"]))
    return eligible[-1]
