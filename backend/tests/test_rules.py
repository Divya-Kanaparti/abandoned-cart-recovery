# from datetime import datetime,timedelta
from app.services.rules import is_abandoned,latest_consent,suppression_reason,choose_attribution

# NOW=datetime(2026,10,30,12)
# def test_abandonment_boundary():
#     c={"last_activity_at":NOW-timedelta(minutes=60),"status":"ACTIVE","has_items":True}
#     assert is_abandoned(c,NOW)
# def test_purchase_prevents_abandonment():
#     c={"last_activity_at":NOW-timedelta(hours=4),"status":"ACTIVE"}
#     assert not is_abandoned(c,NOW,has_purchase=True)
# def test_consent_latest_effective_event():
#     records=[{"channel":"EMAIL","status":"OPTED_IN","effective_at":NOW-timedelta(days=2)},{"channel":"EMAIL","status":"OPTED_OUT","effective_at":NOW-timedelta(days=1)}]
#     assert latest_consent(records,"EMAIL",NOW)=="OPTED_OUT"
# def test_unknown_consent_is_suppressed():
#     reason=suppression_reason("CUS-1",{"cart_id":"C1","status":"ABANDONED"},"EMAIL",[],[],NOW)
#     assert reason=="CONSENT_UNKNOWN"
# def test_attribution_last_click_priority():
#     order={"customer_id":"C1","cart_id":"C1","ordered_at":NOW}
#     interactions=[{"customer_id":"C1","cart_id":"C1","interaction_at":NOW-timedelta(hours=2),"event":"OPENED","send_id":"S1"},{"customer_id":"C1","cart_id":"C1","interaction_at":NOW-timedelta(hours=1),"event":"CLICKED","send_id":"S2"}]
#     assert choose_attribution(order,interactions)["send_id"]=="S2"
# def test_outside_attribution_window():
#     order={"customer_id":"C1","cart_id":"C1","ordered_at":NOW}
#     interactions=[{"customer_id":"C1","cart_id":"C1","interaction_at":NOW-timedelta(days=8),"event":"CLICKED","send_id":"S1"}]
#     assert choose_attribution(order,interactions) is None



from datetime import datetime, timedelta

from app.services.rules import (
    is_abandoned,
    latest_consent,
    suppression_reason,
    choose_attribution,
)

NOW = datetime(2026, 10, 30, 12)


# Abandonment tests

def test_abandonment_boundary():
    c = {
        "last_activity_at": NOW - timedelta(minutes=60),
        "status": "ACTIVE",
        "has_items": True
    }
    assert is_abandoned(c, NOW)


def test_purchase_prevents_abandonment():
    c = {
        "last_activity_at": NOW - timedelta(hours=4),
        "status": "ACTIVE"
    }
    assert not is_abandoned(c, NOW, has_purchase=True)


# Consent tests

def test_consent_latest_effective_event():
    records = [
        {
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW - timedelta(days=2)
        },
        {
            "channel": "EMAIL",
            "status": "OPTED_OUT",
            "effective_at": NOW - timedelta(days=1)
        }
    ]
    assert latest_consent(records, "EMAIL", NOW) == "OPTED_OUT"


def test_unknown_consent_is_suppressed():
    reason = suppression_reason(
        "CUS-1",
        {"cart_id": "C1", "status": "ABANDONED"},
        "EMAIL",
        [],
        [],
        NOW
    )
    assert reason == "CONSENT_UNKNOWN"


def test_opted_in_consent_is_allowed():
    records = [
        {
            "consent_id": 1,
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW - timedelta(days=1),
            "withdrawn_at": None
        }
    ]
    assert latest_consent(records, "EMAIL", NOW) == "OPTED_IN"


def test_withdrawn_consent_is_opted_out():
    records = [
        {
            "consent_id": 1,
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW - timedelta(days=2),
            "withdrawn_at": NOW - timedelta(hours=1)
        }
    ]
    assert latest_consent(records, "EMAIL", NOW) == "OPTED_OUT"


def test_future_withdrawal_does_not_block_earlier_time():
    records = [
        {
            "consent_id": 1,
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW - timedelta(days=2),
            "withdrawn_at": NOW + timedelta(hours=2)
        }
    ]
    assert latest_consent(records, "EMAIL", NOW) == "OPTED_IN"


def test_email_and_sms_consent_are_separate():
    records = [
        {
            "consent_id": 1,
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW - timedelta(days=1),
            "withdrawn_at": None
        },
        {
            "consent_id": 2,
            "channel": "SMS",
            "status": "OPTED_OUT",
            "effective_at": NOW - timedelta(days=1),
            "withdrawn_at": None
        }
    ]

    assert latest_consent(records, "EMAIL", NOW) == "OPTED_IN"
    assert latest_consent(records, "SMS", NOW) == "OPTED_OUT"


def test_future_consent_record_is_ignored():
    records = [
        {
            "consent_id": 1,
            "channel": "EMAIL",
            "status": "OPTED_IN",
            "effective_at": NOW + timedelta(days=1),
            "withdrawn_at": None
        }
    ]
    assert latest_consent(records, "EMAIL", NOW) == "UNKNOWN"


# Attribution tests

def test_attribution_last_click_priority():
    order = {
        "customer_id": "C1",
        "cart_id": "C1",
        "ordered_at": NOW
    }

    interactions = [
        {
            "customer_id": "C1",
            "cart_id": "C1",
            "interaction_at": NOW - timedelta(hours=2),
            "event": "OPENED",
            "send_id": "S1"
        },
        {
            "customer_id": "C1",
            "cart_id": "C1",
            "interaction_at": NOW - timedelta(hours=1),
            "event": "CLICKED",
            "send_id": "S2"
        }
    ]

    assert choose_attribution(order, interactions)["send_id"] == "S2"


def test_outside_attribution_window():
    order = {
        "customer_id": "C1",
        "cart_id": "C1",
        "ordered_at": NOW
    }

    interactions = [
        {
            "customer_id": "C1",
            "cart_id": "C1",
            "interaction_at": NOW - timedelta(days=8),
            "event": "CLICKED",
            "send_id": "S1"
        }
    ]

    assert choose_attribution(order, interactions) is None


def test_frequency_cap_is_channel_specific():
    sends = [
        {"customer_id": "C1", "channel": "SMS", "status": "DELIVERED", "attempted_at": NOW - timedelta(days=1), "cart_id": "C0"},
        {"customer_id": "C1", "channel": "SMS", "status": "DELIVERED", "attempted_at": NOW - timedelta(days=2), "cart_id": "C-1"},
        {"customer_id": "C1", "channel": "SMS", "status": "DELIVERED", "attempted_at": NOW - timedelta(days=3), "cart_id": "C-2"},
    ]
    reason = suppression_reason(
        "C1", {"cart_id": "C2", "status": "ABANDONED"}, "EMAIL",
        [{"channel": "EMAIL", "status": "OPTED_IN", "effective_at": NOW - timedelta(days=1)}],
        sends, NOW,
    )
    assert reason is None


def test_frequency_cap_blocks_fourth_channel_attempt():
    sends = [
        {"customer_id": "C1", "channel": "EMAIL", "status": "DELIVERED", "attempted_at": NOW - timedelta(hours=72), "cart_id": "C0"},
        {"customer_id": "C1", "channel": "EMAIL", "status": "DELIVERED", "attempted_at": NOW - timedelta(hours=48), "cart_id": "C-1"},
        {"customer_id": "C1", "channel": "EMAIL", "status": "DELIVERED", "attempted_at": NOW - timedelta(hours=24), "cart_id": "C-2"},
    ]
    reason = suppression_reason(
        "C1", {"cart_id": "C3", "status": "ABANDONED"}, "EMAIL",
        [{"channel": "EMAIL", "status": "OPTED_IN", "effective_at": NOW - timedelta(days=1)}],
        sends, NOW,
    )
    assert reason == "FREQUENCY_CAP_7D"
