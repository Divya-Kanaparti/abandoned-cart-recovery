
from sqlalchemy import text

from .frequency_cap_service import check_frequency_cap


def get_latest_consent(db, customer_id, channel, now):
    """
    Returns the customer's latest effective consent status.
    Unknown consent is treated as not permitted.
    """

    consent = db.execute(
        text("""
            SELECT
                consent_id,
                status,
                effective_at,
                withdrawn_at
            FROM consents
            WHERE customer_id = :customer_id
              AND channel = :channel
              AND effective_at <= :now
            ORDER BY effective_at DESC, consent_id DESC
            LIMIT 1
        """),
        {
            "customer_id": customer_id,
            "channel": channel,
            "now": now
        }
    ).mappings().first()

    if not consent:
        return "UNKNOWN"

    status = consent["status"]

    # An effective withdrawal overrides the earlier opt-in.
    if (
        status == "OPTED_IN"
        and consent["withdrawn_at"] is not None
        and consent["withdrawn_at"] <= now
    ):
        return "OPTED_OUT"

    return status


def get_suppression_reason(
    db,
    customer_id,
    cart_id,
    channel,
    now,
    max_attempts=3,
    window_days=7,
    min_interval_hours=24
):
    """
    Evaluates all recovery suppression rules.

    Returns:
        None if eligible.
        A reason code if suppressed.
    """

    # 1. Check current consent.
    consent_status = get_latest_consent(
        db,
        customer_id,
        channel,
        now
    )

    if consent_status != "OPTED_IN":
        return f"CONSENT_{consent_status}"

    # 2. Check whether the cart exists and is eligible.
    cart = db.execute(
        text("""
            SELECT status
            FROM carts
            WHERE cart_id = :cart_id
              AND customer_id = :customer_id
        """),
        {
            "cart_id": cart_id,
            "customer_id": customer_id
        }
    ).mappings().first()

    if not cart:
        return "CART_NOT_FOUND"

    if cart["status"] not in ("ABANDONED", "RECOVERY_PENDING"):
        return "CART_NOT_ELIGIBLE"

    # 3. Check for a completed purchase.
    purchase = db.execute(
        text("""
            SELECT order_id
            FROM orders
            WHERE cart_id = :cart_id
              AND order_status = 'COMPLETED'
            LIMIT 1
        """),
        {"cart_id": cart_id}
    ).first()

    if purchase:
        return "ALREADY_PURCHASED"

    # 4. Check duplicate recovery attempts for this cart/channel.
    duplicate = db.execute(
        text("""
            SELECT send_id
            FROM send_attempts
            WHERE cart_id = :cart_id
              AND channel = :channel
              AND status NOT IN ('FAILED', 'SUPPRESSED')
            LIMIT 1
        """),
        {
            "cart_id": cart_id,
            "channel": channel
        }
    ).first()

    if duplicate:
        return "DUPLICATE_CART_RECOVERY"

    # 5. Check frequency cap.
    frequency_reason = check_frequency_cap(
        db=db,
        customer_id=customer_id,
        channel=channel,
        now=now,
        max_attempts=max_attempts,
        window_days=window_days,
        min_interval_hours=min_interval_hours
    )

    if frequency_reason:
        return frequency_reason

    return None
