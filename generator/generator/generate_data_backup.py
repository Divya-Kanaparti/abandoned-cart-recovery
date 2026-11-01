import argparse, csv, json, random, hashlib
from pathlib import Path
from datetime import datetime, timedelta
# from .configuration import SEED, REFERENCE_TIME, PROFILES
from ..configuration import SEED, REFERENCE_TIME, PROFILES
# from configuration import SEED, REFERENCE_TIME, PROFILES

PRODUCTS = [
    ("SKU-100","Wireless Mouse",799),("SKU-101","Mechanical Keyboard",2499),
    ("SKU-102","USB-C Hub",1599),("SKU-103","Laptop Stand",1199),
    ("SKU-104","Noise Cancelling Headphones",4999),("SKU-105","Webcam",2199),
    ("SKU-106","Portable SSD",3499),("SKU-107","Bluetooth Speaker",1899)
]
FIRST = ["Aarav","Diya","Ishita","Rohan","Ananya","Vihaan","Meera","Kabir","Sana","Arjun"]
LAST = ["Sharma","Reddy","Patel","Rao","Khan","Iyer","Gupta","Nair","Das","Verma"]
REF = datetime.fromisoformat(REFERENCE_TIME)

def dump_csv(path, rows):
    if not rows: return
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

def generate(profile, output):
    cfg=PROFILES[profile]; rng=random.Random(SEED); out=Path(output); out.mkdir(parents=True,exist_ok=True)
    n=cfg["customers"]; carts_n=cfg["carts"]; abandoned_n=cfg["abandoned"]; sends_n=cfg["sends"]
    customers=[]; consents=[]; sessions=[]; carts=[]; lines=[]; campaigns=[]; templates=[]; sends=[]; orders=[]; order_lines=[]; attrs=[]; truth=[]; anomalies=[]
    
    for i in range(1, n + 1):
        cid = f"CUS-{i:06d}"
        fn = rng.choice(FIRST)
        ln = rng.choice(LAST)

        customers.append(dict(
            customer_id=cid,
            first_name=fn,
            last_name=ln,
            email=f"{fn.lower()}.{i}@example.test",
            phone=f"+9199{i:07d}",
            email_valid=True,
            phone_valid=True,
            created_at=(REF - timedelta(days=rng.randint(30, 500))).isoformat(sep=" ")
        ))

        for ch in ("EMAIL", "SMS"):
            status = rng.choices(
                ["OPTED_IN", "OPTED_OUT", "UNKNOWN"],
                [0.72, 0.18, 0.10]
            )[0]

            effective_at = REF - timedelta(days=rng.randint(1, 180))

            # Store initial consent
            consents.append(dict(
                consent_id=f"CON-{i:06d}-{ch}-01",
                customer_id=cid,
                channel=ch,
                status=status,
                effective_at=effective_at.isoformat(sep=" "),
                withdrawn_at="",
                source="CHECKOUT" if status == "OPTED_IN" else "PREFERENCE_CENTER"
            ))

            # Generate a later withdrawal for selected opted-in customers
            if status == "OPTED_IN" and rng.random() < 0.15:
                withdrawal_at = REF - timedelta(
                    hours=rng.randint(1, 48)
                )

                if withdrawal_at > effective_at:
                    consents.append(dict(
                        consent_id=f"CON-{i:06d}-{ch}-02",
                        customer_id=cid,
                        channel=ch,
                        status="OPTED_OUT",
                        effective_at=withdrawal_at.isoformat(sep=" "),
                        withdrawn_at=withdrawal_at.isoformat(sep=" "),
                        source="PREFERENCE_CENTER"
                    ))
# for i in range(1,n+1):
    #     cid=f"CUS-{i:06d}"; fn=rng.choice(FIRST); ln=rng.choice(LAST)
    #     customers.append(dict(customer_id=cid,first_name=fn,last_name=ln,email=f"{fn.lower()}.{i}@example.test",phone=f"+9199{i:07d}",email_valid=True,phone_valid=True,created_at=(REF-timedelta(days=rng.randint(30,500))).isoformat(sep=" ")))
    #     for ch in ("EMAIL","SMS"):
    #         status=rng.choices(["OPTED_IN","OPTED_OUT","UNKNOWN"],[.72,.18,.10])[0]
    #         consents.append(dict(consent_id=f"CON-{i:06d}-{ch}",customer_id=cid,channel=ch,status=status,effective_at=(REF-timedelta(days=rng.randint(1,180))).isoformat(sep=" "),withdrawn_at="",source="CHECKOUT" if status=="OPTED_IN" else "PREFERENCE_CENTER"))
    # One session per cart is enough to demonstrate multi-session relationships; customer repeats are allowed.
#     for i in range(1,carts_n+1):
#         # cid=f"CUS-{rng.randint(1,n):06d}"; sid=f"SES-{i:07d}"; created=REF-timedelta(days=rng.randint(0,25),hours=rng.randint(0,23))
#         cid = f"CUS-{rng.randint(1,n):06d}"
#     sid = f"SES-{i:07d}"

#     # Define expected distribution for synthetic data
#     expected_abandoned = i <= abandoned_n

#     if expected_abandoned:
#         # Cart must be old enough to become abandoned
#         created = REF - timedelta(
#             days=rng.randint(4, 25),
#             hours=rng.randint(0, 23)
#         )

#         last_activity = REF - timedelta(
#             hours=rng.randint(2, 72)
#         )

#     else:
#         # Recently active cart
#         created = REF - timedelta(
#             days=rng.randint(0, 25),
#             hours=rng.randint(2, 23)
#         )

#         last_activity = REF - timedelta(
#             minutes=rng.randint(0, 50)
#         )
#         sessions.append(dict(session_id=sid,customer_id=cid,device_type=rng.choice(["DESKTOP","MOBILE","TABLET"]),started_at=created.isoformat(sep=" "),ended_at=(created+timedelta(minutes=rng.randint(5,90))).isoformat(sep=" ")))
#         cart_id=f"CART-2026-{i:06d}"; line_count=rng.randint(1,4); total=0
#         for j in range(line_count):
#             sku,name,price=rng.choice(PRODUCTS); qty=rng.randint(1,3); total+=price*qty
#             lines.append(dict(cart_line_id=f"CL-{i:07d}-{j+1:02d}",cart_id=cart_id,sku=sku,product_name=name,quantity=qty,unit_price=price,updated_at=(created+timedelta(minutes=rng.randint(1,20))).isoformat(sep=" ")))
#         # is_ab=i<=abandoned_n
        
#         # last=REF-timedelta(hours=rng.randint(2,72)) if is_ab else REF-timedelta(minutes=rng.randint(0,50))
#         # status="ABANDONED" if is_ab else "ACTIVE"
#         # Generate realistic cart activity timestamps
#         # last_activity = created + timedelta(minutes=rng.randint(10, 120))
#         inactive_minutes = (
#             REF - last_activity
#         ).total_seconds() / 60
#         is_abandoned = (
#             inactive_minutes >= 60
#             and line_count > 0
#         )
#         last = last_activity
#         status = "ABANDONED" if is_abandoned else "ACTIVE"

#         # Determine abandonment using actual inactivity
#         inactive_minutes = (
#              REF - last_activity
#              ).total_seconds() / 60
#         is_abandoned = (
#             inactive_minutes >= 60
#             and line_count > 0
# )

#         last = last_activity

#         status = "ABANDONED" if is_abandoned else "ACTIVE"


        
#         carts.append(dict(cart_id=cart_id,customer_id=cid,session_id=sid,status=status,currency="INR",cart_total=f"{total:.2f}",created_at=created.isoformat(sep=" "),last_activity_at=last.isoformat(sep=" "),abandoned_at=(
#     (last + timedelta(minutes=60)).isoformat(sep=" ")
#     if is_abandoned else ""
# ),recovered_at="",closed_at=""))
#         truth.append(dict(cart_id=cart_id,expected_abandoned_status=status,expected_consent_eligible="",expected_suppression_decision="",expected_campaign_eligible="",expected_attribution="",expected_anomaly_classification="NONE",expected_revenue_attribution="0.00"))
#     abandoned_count = sum(
#     1 for cart in carts
#     if cart["status"] == "ABANDONED"
# )

#     active_count = sum(
#         1 for cart in carts
#         if cart["status"] == "ACTIVE"
#     )
#     print("Abandoned carts:", abandoned_count)
#     print("Active carts:", active_count)
    
    # One session per cart; customers can have multiple carts
    for i in range(1, carts_n + 1):
        cid = f"CUS-{rng.randint(1, n):06d}"
        sid = f"SES-{i:07d}"

        # Controlled synthetic distribution
        expected_abandoned = i <= abandoned_n

        if expected_abandoned:
            created = REF - timedelta(
                days=rng.randint(4, 25),
                hours=rng.randint(0, 23)
            )
            last_activity = REF - timedelta(
                hours=rng.randint(2, 72)
            )
        else:
            created = REF - timedelta(
                days=rng.randint(0, 25),
                hours=rng.randint(2, 23)
            )
            last_activity = REF - timedelta(
                minutes=rng.randint(0, 50)
            )
                    # Validate cart timestamp ordering
        if not (created <= last_activity <= REF):
            raise ValueError(
                f"Invalid lifecycle timestamps for {sid}"
            )


        # Create session
        # sessions.append(dict(
        #     session_id=sid,
        #     customer_id=cid,
        #     device_type=rng.choice(["DESKTOP", "MOBILE", "TABLET"]),
        #     started_at=created.isoformat(sep=" "),
        #     ended_at=(created + timedelta(minutes=rng.randint(5, 90))).isoformat(sep=" ")
        # ))
                # Create a session around the cart's final activity
        session_duration = timedelta(minutes=rng.randint(5, 90))

        session_start = max(
            created,
            last_activity - session_duration
        )

        session_end = last_activity

        sessions.append(dict(
            session_id=sid,
            customer_id=cid,
            device_type=rng.choice(["DESKTOP", "MOBILE", "TABLET"]),
            started_at=session_start.isoformat(sep=" "),
            ended_at=session_end.isoformat(sep=" ")
        ))

        # Create cart lines
        cart_id = f"CART-2026-{i:06d}"
        line_count = rng.randint(1, 4)
        total = 0

        for j in range(line_count):
            sku, name, price = rng.choice(PRODUCTS)
            qty = rng.randint(1, 3)
            total += price * qty

            lines.append(dict(
                cart_line_id=f"CL-{i:07d}-{j+1:02d}",
                cart_id=cart_id,
                sku=sku,
                product_name=name,
                quantity=qty,
                unit_price=price,
                updated_at=(
                    last_activity - timedelta(minutes=rng.randint(0, 10))
                    ).isoformat(sep=" ")
                # updated_at=(last_activity + timedelta(minutes=rng.randint(0, 10))).isoformat(sep=" ")
            ))

        # Calculate abandonment from actual inactivity
        inactive_minutes = (
            REF - last_activity
        ).total_seconds() / 60

        is_abandoned = (
            inactive_minutes >= 60
            and line_count > 0
        )

        status = "ABANDONED" if is_abandoned else "ACTIVE"

        carts.append(dict(
            cart_id=cart_id,
            customer_id=cid,
            session_id=sid,
            status=status,
            currency="INR",
            cart_total=f"{total:.2f}",
            created_at=created.isoformat(sep=" "),
            last_activity_at=last_activity.isoformat(sep=" "),
            abandoned_at=(
                (last_activity + timedelta(minutes=60)).isoformat(sep=" ")
                if is_abandoned else ""
            ),
            recovered_at="",
            closed_at=""
        ))

        truth.append(dict(
            cart_id=cart_id,
            expected_abandoned_status=status,
            expected_consent_eligible="",
            expected_suppression_decision="",
            expected_campaign_eligible="",
            expected_attribution="",
            expected_anomaly_classification="NONE",
            expected_revenue_attribution="0.00"
        ))

    # Verify generated cart distribution
    abandoned_count = sum(
        1 for cart in carts
        if cart["status"] == "ABANDONED"
    )
    active_count = sum(
        1 for cart in carts
        if cart["status"] == "ACTIVE"
    )

    print("Abandoned carts:", abandoned_count)
    print("Active carts:", active_count)

    # Campaign variants and templates
    # for i,ch in enumerate(["EMAIL","SMS","EMAIL"],1):
    #     cmp=f"CMP-2026-{i:06d}"; variant=["A","B","C"][i-1]
    #     campaigns.append(dict(campaign_id=cmp,campaign_name=f"{['1-hour','6-hour','24-hour'][i-1]} Recovery {ch}",channel=ch,variant=variant,target_audience="ABANDONED_CARTS",scheduled_at=REF.isoformat(sep=" "),status="COMPLETED",created_at=REF.isoformat(sep=" ")))
    #     templates.append(dict(template_id=f"TPL-{i:04d}",campaign_id=cmp,channel=ch,subject="Your cart is waiting" if ch=="EMAIL" else "",body="Hi {{customer_name}}, your cart {{cart_id}} worth {{cart_value}} is waiting. Continue: {{recovery_link}}"))
    #     # Build lookup using the latest consent record per customer and channel
    # consent_lookup = {}

    # for consent in consents:
    #     key = (consent["customer_id"], consent["channel"])

    #     if key not in consent_lookup:
    #         consent_lookup[key] = consent
    #     else:
    #         existing_time = datetime.fromisoformat(
    #             consent_lookup[key]["effective_at"]
    #         )
    #         new_time = datetime.fromisoformat(consent["effective_at"])

    #         if new_time > existing_time:
    #             consent_lookup[key] = consent
    #             # Deterministic send attempts. Only use abandoned carts.
    # for i in range(1,sends_n+1):
    #     # cart=carts[rng.randrange(abandoned_n)];
    #     abandoned_carts = [
    #         cart for cart in carts
    #         if cart["status"] == "ABANDONED"
    #     ]
    #     if not abandoned_carts:
    #         raise ValueError("No abandoned carts available")
    #     cart = rng.choice(abandoned_carts)
    #     channel = rng.choice(["EMAIL", "SMS"])

    #     current_consent = consent_lookup.get(
    #         (cart["customer_id"], channel)
    #     )

    #     eligible = (
    #         current_consent is not None
    #         and current_consent["status"] == "OPTED_IN"
    #     )

    #     cmp_idx = 0 if channel == "EMAIL" else 1
    #     campaign = campaigns[cmp_idx]
    #     template = templates[cmp_idx]
    #     # channel=rng.choice(["EMAIL","SMS"]); cstatus=next(x["status"] for x in consents if x["customer_id"]==cart["customer_id"] and x["channel"]==channel)
    #     # cmp_idx=0 if channel=="EMAIL" else 1; campaign=campaigns[cmp_idx]; template=templates[cmp_idx]
    #     # eligible=cstatus=="OPTED_IN"
    #     status=rng.choice(["DELIVERED","OPENED","CLICKED","BOUNCED"]) if eligible else "SUPPRESSED"
    #     if status in ("OPENED","CLICKED"): event=(REF-timedelta(hours=rng.randint(1,48))).isoformat(sep=" ")
    #     else: event=""
    #     send_id=f"SEND-2026-{i:06d}"
    #     sends.append(dict(send_id=send_id,campaign_id=campaign["campaign_id"],template_id=template["template_id"],customer_id=cart["customer_id"],cart_id=cart["cart_id"],channel=channel,status=status,attempted_at=REF.isoformat(sep=" "),event_at=event,failure_reason="" if eligible else "CONSENT_NOT_OPTED_IN",recovery_link=f"https://shop.example.test/recover/{cart['cart_id']}"))
    #     truth_row=next(t for t in truth if t["cart_id"]==cart["cart_id"])
    #     truth_row["expected_consent_eligible"]="YES" if eligible else "NO"
    #     truth_row["expected_suppression_decision"]="ALLOW" if eligible else "SUPPRESS"
    #     truth_row["expected_campaign_eligible"]="YES" if eligible else "NO"

        # Campaign variants and templates
    campaign_delays = [1, 6, 24]

    for i, ch in enumerate(["EMAIL", "SMS", "EMAIL"], 1):
        cmp = f"CMP-2026-{i:06d}"
        variant = ["A", "B", "C"][i - 1]

        campaigns.append(dict(
            campaign_id=cmp,
            campaign_name=f"{campaign_delays[i-1]}-hour Recovery {ch}",
            channel=ch,
            variant=variant,
            target_audience="ABANDONED_CARTS",
            scheduled_at=(
                REF - timedelta(hours=campaign_delays[i-1])
            ).isoformat(sep=" "),
            status="COMPLETED",
            created_at=(
                REF - timedelta(days=2)
            ).isoformat(sep=" ")
        ))

        templates.append(dict(
            template_id=f"TPL-{i:04d}",
            campaign_id=cmp,
            channel=ch,
            subject="Your cart is waiting" if ch == "EMAIL" else "",
            body=(
                "Hi {{customer_name}}, your cart {{cart_id}} "
                "worth {{cart_value}} is waiting. "
                "Continue: {{recovery_link}}"
            )
        ))

    # Generate deterministic send attempts
        



    abandoned_carts = [
        cart for cart in carts
        if cart["status"] == "ABANDONED"
    ]

    if not abandoned_carts:
        raise ValueError("No abandoned carts available")

    # Create unique cart-campaign combinations.
    # A cart can receive different campaigns, but not the same
    # campaign more than once.
    attempt_slots = [
        (cart, campaign, template)
        for cart in abandoned_carts
        for campaign, template in zip(campaigns, templates)
    ]

    # Randomize the combinations without creating duplicates.
    rng.shuffle(attempt_slots)

    selected_slots = attempt_slots[:min(sends_n, len(attempt_slots))]

    for i, (cart, campaign, template) in enumerate(selected_slots, start=1):

        # Use the channel assigned to the selected campaign.
        channel = campaign["channel"]

    # for i in range(1, sends_n + 1):

    #     abandoned_carts = [
    #         cart for cart in carts
    #         if cart["status"] == "ABANDONED"
    #     ]

    #     if not abandoned_carts:
    #         raise ValueError("No abandoned carts available")

    #     cart = rng.choice(abandoned_carts)
    #     channel = rng.choice(["EMAIL", "SMS"])

    #     campaign_options = [
    #         (campaign, template)
    #         for campaign, template in zip(campaigns, templates)
    #         if campaign["channel"] == channel
    #     ]

    #     campaign, template = rng.choice(campaign_options)

        # attempted_at = datetime.fromisoformat(
        #     cart["abandoned_at"]
        # ) + timedelta(minutes=campaign_delays[
        #     campaigns.index(campaign)
        # ])
        attempted_at = datetime.fromisoformat(
        cart["abandoned_at"]
         ) + timedelta(hours=campaign_delays[
        campaigns.index(campaign)
     ])

        if attempted_at > REF:
            attempted_at = REF

        current_consent = [
            c for c in consents
            if c["customer_id"] == cart["customer_id"]
            and c["channel"] == channel
            and datetime.fromisoformat(c["effective_at"]) <= attempted_at
        ]

        latest_consent = max(
            current_consent,
            key=lambda c: c["effective_at"],
            default=None
        )

        eligible = (
            latest_consent is not None
            and latest_consent["status"] == "OPTED_IN"
        )

        status = (
            rng.choice(["DELIVERED", "OPENED", "CLICKED", "BOUNCED"])
            if eligible
            else "SUPPRESSED"
        )

        event = ""

        if status in ("OPENED", "CLICKED"):
            event_at = attempted_at + timedelta(
                minutes=rng.randint(1, 120)
            )

            if event_at <= REF:
                event = event_at.isoformat(sep=" ")
            else:
                status = "DELIVERED"

        send_id = f"SEND-2026-{i:06d}"

        sends.append(dict(
            send_id=send_id,
            campaign_id=campaign["campaign_id"],
            template_id=template["template_id"],
            customer_id=cart["customer_id"],
            cart_id=cart["cart_id"],
            channel=channel,
            status=status,
            attempted_at=attempted_at.isoformat(sep=" "),
            event_at=event,
            failure_reason="" if eligible else "CONSENT_NOT_OPTED_IN",
            recovery_link=(
                f"https://shop.example.test/recover/{cart['cart_id']}"
            )
        ))

        truth_row = next(
            t for t in truth
            if t["cart_id"] == cart["cart_id"]
        )

        truth_row["expected_consent_eligible"] = (
            "YES" if eligible else "NO"
        )

        truth_row["expected_suppression_decision"] = (
            "ALLOW" if eligible else "SUPPRESS"
        )

        truth_row["expected_campaign_eligible"] = (
            "YES" if eligible else "NO"
        )
            # Apply frequency caps per customer
    customer_send_history = {}

    sorted_sends = sorted(
        sends,
        key=lambda s: (
            datetime.fromisoformat(s["attempted_at"]),
            s["send_id"]
        )
    )

    for send in sorted_sends:

        # Consent-suppressed messages do not enter frequency history
        if send["status"] == "SUPPRESSED":
            continue

        customer_id = send["customer_id"]

        attempted_at = datetime.fromisoformat(
            send["attempted_at"]
        )

        if customer_id not in customer_send_history:
            customer_send_history[customer_id] = []

        history = customer_send_history[customer_id]

        recent_24h = [
            previous for previous in history
            if previous > attempted_at - timedelta(hours=24)
        ]

        recent_7d = [
            previous for previous in history
            if previous > attempted_at - timedelta(days=7)
        ]

        if len(recent_24h) >= 2 or len(recent_7d) >= 3:

            send["status"] = "SUPPRESSED"
            send["event_at"] = ""
            send["failure_reason"] = "FREQUENCY_CAP_EXCEEDED"

            truth_row = next(
                t for t in truth
                if t["cart_id"] == send["cart_id"]
            )

            truth_row["expected_suppression_decision"] = "SUPPRESS"
            truth_row["expected_campaign_eligible"] = "NO"

        else:
            history.append(attempted_at)
    # Orders for a subset of carts; totals calculated from their cart lines.
        # Generate orders with realistic purchase timestamps
        
    # Generate orders for a subset of carts
    # orderable_carts = rng.sample(
    #     carts,
    #     min(carts_n // 5, 5000)
    # )

    # for i, cart in enumerate(orderable_carts, 1):

    #     cl = [
    #         x for x in lines
    #         if x["cart_id"] == cart["cart_id"]
    #     ]

    #     # Calculate order total from cart lines
    #     total = sum(
    #         int(x["quantity"]) * float(x["unit_price"])
    #         for x in cl
    #     )

    #     created_at = datetime.fromisoformat(cart["created_at"])
    #     last_activity = datetime.fromisoformat(
    #         cart["last_activity_at"]
    #     )

    #     # Generate purchase after the cart's last activity
    #     available_seconds = int(
    #         (REF - last_activity).total_seconds()
    #     )

    #     purchase_delay = rng.randint(
    #         0, max(0, available_seconds)
    #     )

    #     ordered = last_activity + timedelta(
    #         seconds=purchase_delay
    #     )

    #     # Calculate the actual abandonment threshold
    #     abandonment_time = last_activity + timedelta(minutes=60)

    #     # Determine the final cart lifecycle state
    #     if ordered >= abandonment_time and abandonment_time <= REF:
    #         final_status = "RECOVERED"
    #         cart["abandoned_at"] = abandonment_time.isoformat(sep=" ")
    #         cart["recovered_at"] = ordered.isoformat(sep=" ")
    #     else:
    #         final_status = "PURCHASED"
    #         cart["abandoned_at"] = ""

    #     cart["status"] = final_status
    #     cart["closed_at"] = ordered.isoformat(sep=" ")

    #     oid = f"ORD-{i:06d}"

    # #     orders.append(dict(
    # #         order_id=oid,
    # #         customer_id=cart["customer_id"],
    # #         cart_id=cart["cart_id"],
    # #         order_status="COMPLETED",
    # #         order_total=f"{total:.2f}",
    # #         ordered_at=ordered.isoformat(sep=" ")
    # #     ))
    # #         # Suppress recovery messages if the customer already purchased
    # # order_lookup = {
    # #     order["cart_id"]: order
    # #     for order in orders
    # # }

    # # for send in sends:
    # #     order = order_lookup.get(send["cart_id"])

    # #     if order:
    # #         ordered_at = datetime.fromisoformat(
    # #             order["ordered_at"]
    # #         )

    # #         attempted_at = datetime.fromisoformat(
    # #             send["attempted_at"]
    # #         )

    # #         if ordered_at <= attempted_at:
    # #             send["status"] = "SUPPRESSED"
    # #             send["failure_reason"] = "PURCHASE_ALREADY_COMPLETED"

    # #             truth_row = next(
    # #                 t for t in truth
    # #                 if t["cart_id"] == send["cart_id"]
    # #             )

    # #             truth_row["expected_suppression_decision"] = "SUPPRESS"
    # #             truth_row["expected_campaign_eligible"] = "NO"
    
    #     orders.append(dict(
    #         order_id=oid,
    #         customer_id=cart["customer_id"],
    #         cart_id=cart["cart_id"],
    #         order_status="COMPLETED",
    #         order_total=f"{total:.2f}",
    #         ordered_at=ordered.isoformat(sep=" ")
    #     ))

    #     # Update separate ground truth
    #     truth_row = next(
    #         t for t in truth
    #         if t["cart_id"] == cart["cart_id"]
    #     )
    #     truth_row["expected_abandoned_status"] = final_status

    #     # Generate order lines
    #     for j, x in enumerate(cl, 1):
    #         order_lines.append(dict(
    #             order_line_id=f"OL-{i:06d}-{j:02d}",
    #             order_id=oid,
    #             sku=x["sku"],
    #             product_name=x["product_name"],
    #             quantity=x["quantity"],
    #             unit_price=x["unit_price"]
    #         ))

    # # Suppress recovery messages if the customer already purchased
    # order_lookup = {
    #     order["cart_id"]: order
    #     for order in orders
    # }

    # for send in sends:
    #     order = order_lookup.get(send["cart_id"])

    #     if order:
    #         ordered_at = datetime.fromisoformat(order["ordered_at"])
    #         attempted_at = datetime.fromisoformat(send["attempted_at"])

    #         if ordered_at <= attempted_at:
    #             send["status"] = "SUPPRESSED"
    #             send["failure_reason"] = "PURCHASE_ALREADY_COMPLETED"

    #             truth_row = next(
    #                 t for t in truth
    #                 if t["cart_id"] == send["cart_id"]
    #             )
    #             truth_row["expected_suppression_decision"] = "SUPPRESS"
    #             truth_row["expected_campaign_eligible"] = "NO"

    
    # Generate orders for a subset of carts
    orderable_carts = rng.sample(
        carts,
        min(carts_n // 5, 5000)
    )

    for i, cart in enumerate(orderable_carts, 1):

        cl = [
            x for x in lines
            if x["cart_id"] == cart["cart_id"]
        ]

        # Calculate order total from cart lines
        total = sum(
            int(x["quantity"]) * float(x["unit_price"])
            for x in cl
        )

        last_activity = datetime.fromisoformat(
            cart["last_activity_at"]
        )

        abandonment_time = last_activity + timedelta(minutes=60)

        # Find valid campaign clicks for this cart
        cart_clicks = [
            send for send in sends
            if send["cart_id"] == cart["cart_id"]
            and send["status"] == "CLICKED"
            and send["event_at"]
        ]

        # Generate purchase time after the latest click
        if cart_clicks:
            latest_click = max(
                cart_clicks,
                key=lambda s: s["event_at"]
            )

            click_time = datetime.fromisoformat(
                latest_click["event_at"]
            )

            remaining_seconds = int(
                (REF - click_time).total_seconds()
            )

            if remaining_seconds > 0:
                ordered = click_time + timedelta(
                    seconds=rng.randint(1, remaining_seconds)
                )
            else:
                available_seconds = max(
                    0,
                    int((REF - last_activity).total_seconds())
                )
                ordered = last_activity + timedelta(
                    seconds=rng.randint(0, available_seconds)
                )
        else:
            available_seconds = max(
                0,
                int((REF - last_activity).total_seconds())
            )

            ordered = last_activity + timedelta(
                seconds=rng.randint(0, available_seconds)
            )

        # Find campaign clicks within the 7-day attribution window
        eligible_clicks = []

        for send in sends:
            if (
                send["cart_id"] != cart["cart_id"]
                or send["status"] != "CLICKED"
                or not send["event_at"]
            ):
                continue

            attempted_at = datetime.fromisoformat(
                send["attempted_at"]
            )

            event_at = datetime.fromisoformat(
                send["event_at"]
            )

            if (
                attempted_at <= event_at <= ordered
                and ordered - timedelta(days=7) <= event_at
            ):
                eligible_clicks.append(send)

        # Last-touch attribution: choose the latest eligible click
        attributed_send = (
            max(
                eligible_clicks,
                key=lambda s: s["event_at"]
            )
            if eligible_clicks
            else None
        )

        # Determine the correct cart lifecycle state
        if ordered >= abandonment_time and abandonment_time <= REF:
            cart["abandoned_at"] = abandonment_time.isoformat(sep=" ")

            if attributed_send:
                final_status = "RECOVERED"
                cart["recovered_at"] = ordered.isoformat(sep=" ")
            else:
                # Organic purchase after abandonment
                final_status = "PURCHASED"
                cart["recovered_at"] = ""
        else:
            final_status = "PURCHASED"
            cart["abandoned_at"] = ""
            cart["recovered_at"] = ""

        cart["status"] = final_status
        cart["closed_at"] = ordered.isoformat(sep=" ")

        oid = f"ORD-{i:06d}"

        # Create order
        orders.append(dict(
            order_id=oid,
            customer_id=cart["customer_id"],
            cart_id=cart["cart_id"],
            order_status="COMPLETED",
            order_total=f"{total:.2f}",
            ordered_at=ordered.isoformat(sep=" ")
        ))

        # Generate order lines
        for j, x in enumerate(cl, 1):
            order_lines.append(dict(
                order_line_id=f"OL-{i:06d}-{j:02d}",
                order_id=oid,
                sku=x["sku"],
                product_name=x["product_name"],
                quantity=x["quantity"],
                unit_price=x["unit_price"]
            ))

        # Update ground truth
        truth_row = next(
            t for t in truth
            if t["cart_id"] == cart["cart_id"]
        )

        truth_row["expected_abandoned_status"] = final_status

        if attributed_send:
            # Create one LAST_TOUCH_7D attribution per order
            attrs.append(dict(
                attribution_id=f"ATTR-{len(attrs) + 1:07d}",
                order_id=oid,
                customer_id=cart["customer_id"],
                cart_id=cart["cart_id"],
                campaign_id=attributed_send["campaign_id"],
                send_id=attributed_send["send_id"],
                model="LAST_TOUCH_7D",
                attributed_at=ordered.isoformat(sep=" "),
                attributed_revenue=f"{total:.2f}",
                reason="Latest eligible campaign click within 7 days before purchase"
            ))

            truth_row["expected_attribution"] = "LAST_TOUCH_7D"
            truth_row["expected_revenue_attribution"] = f"{total:.2f}"
        else:
            truth_row["expected_attribution"] = "NONE"
            truth_row["expected_revenue_attribution"] = "0.00"

    # Suppress messages attempted after a completed purchase
    order_lookup = {
        order["cart_id"]: order
        for order in orders
    }

    for send in sends:
        order = order_lookup.get(send["cart_id"])

        if not order:
            continue

        ordered_at = datetime.fromisoformat(
            order["ordered_at"]
        )

        attempted_at = datetime.fromisoformat(
            send["attempted_at"]
        )

        if ordered_at <= attempted_at:
            send["status"] = "SUPPRESSED"
            send["event_at"] = ""
            send["failure_reason"] = "PURCHASE_ALREADY_COMPLETED"

            truth_row = next(
                t for t in truth
                if t["cart_id"] == send["cart_id"]
            )

            truth_row["expected_suppression_decision"] = "SUPPRESS"
            truth_row["expected_campaign_eligible"] = "NO"

    # Mark carts without attribution explicitly
    for truth_row in truth:
        if not truth_row["expected_attribution"]:
            truth_row["expected_attribution"] = "NONE"



        # Update separate ground truth
        # truth_row = next(
        #     t for t in truth
        #     if t["cart_id"] == cart["cart_id"]
        # )

        # truth_row["expected_abandoned_status"] = final_status

        # # Generate order lines
        # for j, x in enumerate(cl, 1):
        #     order_lines.append(dict(
        #         order_line_id=f"OL-{i:06d}-{j:02d}",
        #         order_id=oid,
        #         sku=x["sku"],
        #         product_name=x["product_name"],
        #         quantity=x["quantity"],
        #         unit_price=x["unit_price"]
        #     ))

    # orderable_carts = rng.sample(
    #     carts,
    #     min(carts_n // 5, 5000)
    # )

    # for i, cart in enumerate(orderable_carts, 1):

    #     cl = [
    #         x for x in lines
    #         if x["cart_id"] == cart["cart_id"]
    #     ]

    #     total = sum(
    #         int(x["quantity"]) * float(x["unit_price"])
    #         for x in cl
    #     )

    #     # Orders happen after cart creation
    #     created_at = datetime.fromisoformat(cart["created_at"])
    #     ordered = created_at + timedelta(
    #         hours=rng.randint(1, 72)
    #     )

    #     # Keep order time within the reference time
    #     if ordered > REF:
    #         ordered = REF - timedelta(minutes=1)

    #     oid = f"ORD-{i:06d}"

    #     orders.append(dict(
    #         order_id=oid,
    #         customer_id=cart["customer_id"],
    #         cart_id=cart["cart_id"],
    #         order_status="COMPLETED",
    #         order_total=f"{total:.2f}",
    #         ordered_at=ordered.isoformat(sep=" ")
    #     ))

    #     # Update cart lifecycle after purchase
    #     cart["status"] = "RECOVERED"
    #     cart["recovered_at"] = ordered.isoformat(sep=" ")
    #     cart["closed_at"] = ordered.isoformat(sep=" ")

    #     for j, x in enumerate(cl, 1):
    #         order_lines.append(dict(
    #             order_line_id=f"OL-{i:06d}-{j:02d}",
    #             order_id=oid,
    #             sku=x["sku"],
    #             product_name=x["product_name"],
    #             quantity=x["quantity"],
    #             unit_price=x["unit_price"]
    #         ))
    # orderable_carts=rng.sample(carts, min(carts_n//5, 5000))
    # for i, cart in enumerate(orderable_carts, 1):
    #     cl=[x for x in lines if x["cart_id"]==cart["cart_id"]]
    #     total=sum(int(x["quantity"])*float(x["unit_price"]) for x in cl)
    #     oid=f"ORD-{i:06d}"; ordered=REF-timedelta(hours=rng.randint(1,240))
    #     orders.append(dict(order_id=oid,customer_id=cart["customer_id"],cart_id=cart["cart_id"],order_status="COMPLETED",order_total=f"{total:.2f}",ordered_at=ordered.isoformat(sep=" ")))
    #     for j,x in enumerate(cl,1):
    #         order_lines.append(dict(order_line_id=f"OL-{i:06d}-{j:02d}",order_id=oid,sku=x["sku"],product_name=x["product_name"],quantity=x["quantity"],unit_price=x["unit_price"]))
    
    # Generate audit decision records
    audit_decisions = []

    for send in sends:
        reason = send["failure_reason"]

        if send["status"] == "SUPPRESSED":
            decision = "SUPPRESSED"
            reason_code = reason or "OTHER_SUPPRESSION"

            detail_messages = {
                "CONSENT_NOT_OPTED_IN": "Customer did not have valid opt-in consent for this channel.",
                "FREQUENCY_CAP_EXCEEDED": "Customer exceeded the permitted recovery message frequency.",
                "PURCHASE_ALREADY_COMPLETED": "Recovery message suppressed because the customer had already purchased."
            }

            detail = detail_messages.get(
                reason_code,
                "Message was suppressed by a business rule."
            )

        else:
            decision = "ELIGIBLE"
            reason_code = "ALL_CHECKS_PASSED"
            detail = "Consent and frequency checks passed at the time of the attempt."

        audit_decisions.append(dict(
            decision_id=f"DEC-{len(audit_decisions) + 1:07d}",
            customer_id=send["customer_id"],
            cart_id=send["cart_id"],
            channel=send["channel"],
            decision=decision,
            reason_code=reason_code,
            detail=detail,
            decided_at=send["attempted_at"]
        ))

    # Generate cart event history
    cart_events = []

    event_priority = {
        "CREATED": 0,
        "ITEM_ADDED": 1,
        "QUANTITY_UPDATED": 2,
        "ITEM_REMOVED": 3,
        "ABANDONED": 4,
        "RECOVERED": 5,
        "CLOSED": 6
    }

    for cart in carts:

        cart_id = cart["cart_id"]

        # Cart creation event
        cart_events.append(dict(
            cart_id=cart_id,
            event_type="CREATED",
            event_at=cart["created_at"],
            details=json.dumps({"source": "CART_CREATION"})
        ))

        # Product addition events
        cart_items = [
            line for line in lines
            if line["cart_id"] == cart_id
        ]

        for line in cart_items:
            cart_events.append(dict(
                cart_id=cart_id,
                event_type="ITEM_ADDED",
                event_at=line["updated_at"],
                details=json.dumps({
                    "cart_line_id": line["cart_line_id"],
                    "sku": line["sku"],
                    "quantity": line["quantity"]
                })
            ))

        # Cart abandonment event
        if cart["abandoned_at"]:
            cart_events.append(dict(
                cart_id=cart_id,
                event_type="ABANDONED",
                event_at=cart["abandoned_at"],
                details=json.dumps({"reason": "60_MINUTES_INACTIVITY"})
            ))

        # Successful recovery event
        if cart["recovered_at"]:
            cart_events.append(dict(
                cart_id=cart_id,
                event_type="RECOVERED",
                event_at=cart["recovered_at"],
                details=json.dumps({"source": "CAMPAIGN_ATTRIBUTION"})
            ))

        # Cart closure event
        if cart["closed_at"]:
            cart_events.append(dict(
                cart_id=cart_id,
                event_type="CLOSED",
                event_at=cart["closed_at"],
                details=json.dumps({
                    "final_status": cart["status"]
                })
            ))

    # Keep events in chronological order
    cart_events.sort(
        key=lambda event: (
            event["cart_id"],
            datetime.fromisoformat(event["event_at"]),
            event_priority[event["event_type"]]
        )
    )
    # Assign deterministic unique event IDs after sorting
    for index, event in enumerate(cart_events, start=1):
        event["event_id"] = f"EVT-{index:07d}"

# Inject labelled issues into separate anomaly file, not by silently damaging baseline rows.
    # anomalies=[
    #   dict(issue_type="MESSAGE_AFTER_OPTOUT",ground_truth="CONSENT_WITHDRAWN",expected_decision="BLOCK_SEND",actual_decision="SEND_RECORDED",affected_entity_id="CUS-000001",description="Synthetic negative test fixture: attempted communication follows an opt-out event."),
    #   dict(issue_type="PURCHASE_BEFORE_ABANDONMENT",ground_truth="ORDER_PRECEDES_EVALUATION",expected_decision="NOT_ABANDONED",actual_decision="ABANDONED",affected_entity_id="CART-2026-000001",description="Synthetic negative test fixture: cart must not be abandoned after a qualifying purchase."),
    #   dict(issue_type="DUPLICATE_ATTRIBUTION",ground_truth="ONE_ORDER_ONE_CREDIT",expected_decision="FLAG_DUPLICATE",actual_decision="MULTIPLE_CAMPAIGNS_CREDITED",affected_entity_id="ORD-000001",description="Synthetic negative test fixture: the same order is credited to competing campaigns."),
    #   dict(issue_type="STALE_CART_TOTAL",ground_truth="LINE_SUM_IS_SOURCE_OF_TRUTH",expected_decision="RECALCULATE_TOTAL",actual_decision="STALE_TOTAL_RETAINED",affected_entity_id="CART-2026-000002",description="Synthetic negative test fixture: quantity changed without updating the denormalized cart total.")
    # ]
    anomalies = [
    dict(
        issue_type="MESSAGE_AFTER_OPTOUT",
        ground_truth="CONSENT_WITHDRAWN",
        expected_decision="BLOCK_SEND",
        actual_decision="SEND_RECORDED",
        affected_entity_id="CUS-000001",
        description="Synthetic negative test fixture: attempted communication follows an opt-out event.",
        detected_at=REFERENCE_TIME.replace("T", " ")
    ),
    dict(
        issue_type="PURCHASE_BEFORE_ABANDONMENT",
        ground_truth="ORDER_PRECEDES_EVALUATION",
        expected_decision="NOT_ABANDONED",
        actual_decision="ABANDONED",
        affected_entity_id="CART-2026-000001",
        description="Synthetic negative test fixture: cart must not be abandoned after a qualifying purchase.",
        detected_at=REFERENCE_TIME.replace("T", " ")
    ),
    dict(
        issue_type="DUPLICATE_ATTRIBUTION",
        ground_truth="ONE_ORDER_ONE_CREDIT",
        expected_decision="FLAG_DUPLICATE",
        actual_decision="MULTIPLE_CAMPAIGNS_CREDITED",
        affected_entity_id="ORD-000001",
        description="Synthetic negative test fixture: the same order is credited to competing campaigns.",
        detected_at=REFERENCE_TIME.replace("T", " ")
    ),
    dict(
        issue_type="STALE_CART_TOTAL",
        ground_truth="LINE_SUM_IS_SOURCE_OF_TRUTH",
        expected_decision="RECALCULATE_TOTAL",
        actual_decision="STALE_TOTAL_RETAINED",
        affected_entity_id="CART-2026-000002",
        description="Synthetic negative test fixture: quantity changed without updating the denormalized cart total.",
        detected_at=REFERENCE_TIME.replace("T", " ")
    )
]
    # tables={"customers":customers,"consents":consents,"sessions":sessions,"carts":carts,"cart_lines":lines,"campaigns":campaigns,"message_templates":templates,"send_attempts":sends,"orders":orders,"order_lines":order_lines,"attributions":attrs,"ground_truth":truth,"anomalies":anomalies}
    tables = {
        "customers": customers,
        "consents": consents,
        "sessions": sessions,
        "carts": carts,
        "cart_lines": lines,
        "campaigns": campaigns,
        "message_templates": templates,
        "send_attempts": sends,
        "orders": orders,
        "order_lines": order_lines,
        "attributions": attrs,
        "audit_decisions": audit_decisions,
        "cart_events": cart_events,
        "ground_truth": truth,
        "anomalies": anomalies
    }
    for name,rows in tables.items():
        dump_csv(out/f"{name}.csv",rows)
        (out/f"{name}.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
    report={"profile":profile,"seed":SEED,"reference_time":REFERENCE_TIME,"row_counts":{k:len(v) for k,v in tables.items()}}
    (out/"generation_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--profile",choices=PROFILES,default="starter"); p.add_argument("--output",default="data/starter")
    a=p.parse_args(); generate(a.profile,a.output)
