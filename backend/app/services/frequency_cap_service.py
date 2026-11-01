
from datetime import timedelta
from sqlalchemy import text


def check_frequency_cap(
    db,
    customer_id,
    channel,
    now,
    max_attempts=3,
    window_days=7,
    min_interval_hours=24
):
    """
    Checks whether a customer can receive another recovery message.

    Rules:
    - Maximum 3 attempts per channel in 7 days.
    - Minimum 24 hours between attempts.
    - Failed and suppressed attempts do not count.
    """

    cutoff = now - timedelta(days=window_days)

    rows = db.execute(
        text("""
            SELECT send_id, cart_id, attempted_at, status
            FROM send_attempts
            WHERE customer_id = :customer_id
              AND channel = :channel
              AND attempted_at >= :cutoff
              AND status NOT IN ('FAILED', 'SUPPRESSED')
            ORDER BY attempted_at DESC
        """),
        {
            "customer_id": customer_id,
            "channel": channel,
            "cutoff": cutoff
        }
    ).mappings().all()

    # Check maximum attempts in the rolling window.
    if len(rows) >= max_attempts:
        return "FREQUENCY_CAP_7D"

    # Check minimum interval between attempts.
    if rows:
        latest_attempt = rows[0]["attempted_at"]

        if now - latest_attempt < timedelta(
            hours=min_interval_hours
        ):
            return "MINIMUM_INTERVAL_NOT_MET"

    return None
