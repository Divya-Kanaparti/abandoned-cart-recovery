
from datetime import datetime, timedelta
import json

from sqlalchemy import text

from .suppression_service import get_suppression_reason


def generate_send_id(db, now):
    """
    Generates deterministic-format SEND IDs.
    """

    prefix = f"SEND-{now.year}-"

    result = db.execute(
        text("""
            SELECT COALESCE(
                MAX(CAST(SUBSTRING(send_id, 11) AS UNSIGNED)),
                0
            )
            FROM send_attempts
            WHERE send_id LIKE :prefix
        """),
        {"prefix": prefix + "%"}
    ).scalar()

    next_number = int(result or 0) + 1

    return f"{prefix}{next_number:06d}"


def detect_abandoned_carts(db, now, abandonment_minutes=60, limit=500):
    """
    Changes inactive ACTIVE carts to ABANDONED.

    A cart with a completed purchase is never marked abandoned.
    """

    cutoff = now - timedelta(minutes=abandonment_minutes)

    carts = db.execute(
        text("""
            SELECT c.cart_id, c.customer_id, c.last_activity_at
            FROM carts c
            WHERE c.status = 'ACTIVE'
              AND c.last_activity_at <= :cutoff
              AND NOT EXISTS (
                  SELECT 1
                  FROM orders o
                  WHERE o.cart_id = c.cart_id
                    AND o.order_status = 'COMPLETED'
              )
            ORDER BY c.last_activity_at
            LIMIT :limit
            FOR UPDATE
        """),
        {
            "cutoff": cutoff,
            "limit": limit
        }
    ).mappings().all()

    detected = 0

    for cart in carts:
        abandoned_at = cart["last_activity_at"] + timedelta(
            minutes=abandonment_minutes
        )

        db.execute(
            text("""
                UPDATE carts
                SET status = 'ABANDONED',
                    abandoned_at = :abandoned_at
                WHERE cart_id = :cart_id
                  AND status = 'ACTIVE'
            """),
            {
                "abandoned_at": abandoned_at,
                "cart_id": cart["cart_id"]
            }
        )

        db.execute(
            text("""
                INSERT INTO cart_events (
                    cart_id,
                    event_type,
                    event_at,
                    details
                )
                VALUES (
                    :cart_id,
                    'ABANDONED',
                    :event_at,
                    :details
                )
            """),
            {
                "cart_id": cart["cart_id"],
                "event_at": now,
                "details": json.dumps({
                    "reason": "INACTIVITY_THRESHOLD_REACHED",
                    "abandonment_minutes": abandonment_minutes
                })
            }
        )

        detected += 1

    return detected


def run_recovery_workflow(
    db,
    campaign_id,
    now=None,
    limit=500,
    dry_run=True,
    abandonment_minutes=60
):
    """
    Main abandoned cart recovery workflow.

    dry_run=True:
        Evaluates carts and records decisions without creating sends.

    dry_run=False:
        Creates simulated sends and send events.
    """

    now = now or datetime.now()

    # 1. Validate campaign.
    campaign = db.execute(
        text("""
            SELECT *
            FROM campaigns
            WHERE campaign_id = :campaign_id
        """),
        {"campaign_id": campaign_id}
    ).mappings().first()

    if not campaign:
        raise ValueError("CAMPAIGN_NOT_FOUND")

    if campaign["status"] not in ("SCHEDULED", "RUNNING"):
        raise ValueError(
            "CAMPAIGN_NOT_ACTIVE: campaign must be SCHEDULED or RUNNING"
        )

    if campaign["scheduled_at"] > now:
        raise ValueError("CAMPAIGN_NOT_DUE")

    channel = campaign["channel"]

    # 2. Find the campaign's message template.
    template = db.execute(
        text("""
            SELECT template_id, subject, body
            FROM message_templates
            WHERE campaign_id = :campaign_id
              AND channel = :channel
            LIMIT 1
        """),
        {
            "campaign_id": campaign_id,
            "channel": channel
        }
    ).mappings().first()

    if not template:
        raise ValueError("MESSAGE_TEMPLATE_NOT_FOUND")

    # 3. Detect newly abandoned carts.
    newly_abandoned = detect_abandoned_carts(
        db,
        now,
        abandonment_minutes,
        limit
    )

    # 4. Retrieve eligible cart candidates.
    cutoff = now - timedelta(minutes=abandonment_minutes)

    carts = db.execute(
        text("""
            SELECT
                c.cart_id,
                c.customer_id,
                c.cart_total,
                c.status,
                cu.first_name,
                cu.last_name
            FROM carts c
            JOIN customers cu
                ON cu.customer_id = c.customer_id
            WHERE c.status IN ('ABANDONED', 'RECOVERY_PENDING')
              AND c.last_activity_at <= :cutoff
              AND NOT EXISTS (
                  SELECT 1
                  FROM orders o
                  WHERE o.cart_id = c.cart_id
                    AND o.order_status = 'COMPLETED'
              )
            ORDER BY c.abandoned_at, c.cart_id
            LIMIT :limit
            FOR UPDATE
        """),
        {
            "cutoff": cutoff,
            "limit": limit
        }
    ).mappings().all()

    summary = {
        "campaign_id": campaign_id,
        "channel": channel,
        "total_checked": 0,
        "newly_abandoned": newly_abandoned,
        "eligible": 0,
        "suppressed": 0,
        "messages_created": 0,
        "dry_run": dry_run,
        "decisions": []
    }

    # 5. Evaluate each cart.
    for cart in carts:

        summary["total_checked"] += 1

        reason = get_suppression_reason(
            db=db,
            customer_id=cart["customer_id"],
            cart_id=cart["cart_id"],
            channel=channel,
            now=now
        )

        if reason:
            decision = "SUPPRESSED"
            summary["suppressed"] += 1
        else:
            decision = "ELIGIBLE"
            summary["eligible"] += 1

        # 6. Record every decision.
        db.execute(
            text("""
                INSERT INTO audit_decisions (
                    customer_id,
                    cart_id,
                    channel,
                    decision,
                    reason_code,
                    detail,
                    decided_at
                )
                VALUES (
                    :customer_id,
                    :cart_id,
                    :channel,
                    :decision,
                    :reason_code,
                    :detail,
                    :decided_at
                )
            """),
            {
                "customer_id": cart["customer_id"],
                "cart_id": cart["cart_id"],
                "channel": channel,
                "decision": decision,
                "reason_code": reason or "ALL_RULES_PASSED",
                "detail": (
                    "Dry-run evaluation"
                    if dry_run
                    else "Recovery workflow evaluation"
                ),
                "decided_at": now
            }
        )

        summary["decisions"].append({
            "cart_id": cart["cart_id"],
            "customer_id": cart["customer_id"],
            "decision": decision,
            "reason": reason or "ALL_RULES_PASSED"
        })

        # 7. Stop here during preview mode.
        if reason or dry_run:
            continue

        # 8. Recheck consent immediately before creating a send.
        final_reason = get_suppression_reason(
            db=db,
            customer_id=cart["customer_id"],
            cart_id=cart["cart_id"],
            channel=channel,
            now=now
        )

        if final_reason:
            summary["suppressed"] += 1

            db.execute(
                text("""
                    INSERT INTO audit_decisions (
                        customer_id,
                        cart_id,
                        channel,
                        decision,
                        reason_code,
                        detail,
                        decided_at
                    )
                    VALUES (
                        :customer_id,
                        :cart_id,
                        :channel,
                        'BLOCKED',
                        :reason_code,
                        'Final pre-dispatch consent and suppression check',
                        :now
                    )
                """),
                {
                    "customer_id": cart["customer_id"],
                    "cart_id": cart["cart_id"],
                    "channel": channel,
                    "reason_code": final_reason,
                    "now": now
                }
            )

            continue

        # 9. Generate a unique send ID.
        send_id = generate_send_id(db, now)

        recovery_link = (
            f"https://shop.example.test/recover/{cart['cart_id']}"
        )

        # 10. Create a simulated send attempt.
        db.execute(
            text("""
                INSERT INTO send_attempts (
                    send_id,
                    campaign_id,
                    template_id,
                    customer_id,
                    cart_id,
                    channel,
                    status,
                    attempted_at,
                    event_at,
                    recovery_link
                )
                VALUES (
                    :send_id,
                    :campaign_id,
                    :template_id,
                    :customer_id,
                    :cart_id,
                    :channel,
                    'SENT',
                    :now,
                    :now,
                    :recovery_link
                )
            """),
            {
                "send_id": send_id,
                "campaign_id": campaign_id,
                "template_id": template["template_id"],
                "customer_id": cart["customer_id"],
                "cart_id": cart["cart_id"],
                "channel": channel,
                "now": now,
                "recovery_link": recovery_link
            }
        )

        # 11. Record the SENT event.
        db.execute(
            text("""
                INSERT INTO send_events (
                    send_id,
                    event_type,
                    event_at,
                    event_metadata
                )
                VALUES (
                    :send_id,
                    'SENT',
                    :now,
                    :metadata
                )
            """),
            {
                "send_id": send_id,
                "now": now,
                "metadata": json.dumps({
                    "provider": "SIMULATED",
                    "campaign_variant": campaign["variant"]
                })
            }
        )

        # 12. Update cart lifecycle.
        db.execute(
            text("""
                UPDATE carts
                SET status = 'RECOVERY_PENDING'
                WHERE cart_id = :cart_id
            """),
            {"cart_id": cart["cart_id"]}
        )

        summary["messages_created"] += 1

    return summary
