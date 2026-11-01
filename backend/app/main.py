from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from .db import get_db
from datetime import datetime
from typing import Literal
from pydantic import BaseModel
import os

app=FastAPI(title="Abandoned Cart Recovery API",version="1.0.0",description="Consent-aware cart recovery and attribution")
origins=os.getenv("CORS_ORIGINS","http://localhost:5173").split(",")
# app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/api/health")
def health(): return {"status":"ok","database":"MySQL","service":"abandoned-cart-recovery"}

@app.get("/api/dashboard")
def dashboard(db:Session=Depends(get_db)):
    try:
        q=lambda sql: db.execute(text(sql)).scalar() or 0
        return {
          "customers":q("SELECT COUNT(*) FROM customers"),
          "carts":q("SELECT COUNT(*) FROM carts"),
          "active_carts":q("SELECT COUNT(*) FROM carts WHERE status='ACTIVE'"),
          "abandoned_carts":q("SELECT COUNT(*) FROM carts WHERE status='ABANDONED'"),
          "recovered_carts":q("SELECT COUNT(*) FROM carts WHERE status='RECOVERED'"),
          "campaigns":q("SELECT COUNT(*) FROM campaigns"),
          "messages_attempted":q("SELECT COUNT(*) FROM send_attempts"),
          "messages_delivered":q("SELECT COUNT(*) FROM send_attempts WHERE status IN ('DELIVERED','OPENED','CLICKED')"),
          "messages_opened":q("SELECT COUNT(*) FROM send_attempts WHERE status IN ('OPENED','CLICKED')"),
          "messages_clicked":q("SELECT COUNT(*) FROM send_attempts WHERE status='CLICKED'"),
          "orders":q("SELECT COUNT(*) FROM orders"),
          "attributed_orders":q("SELECT COUNT(*) FROM attributions"),
          "recovered_revenue":float(q("SELECT COALESCE(SUM(attributed_revenue),0) FROM attributions"))
        }
    except Exception as e:
        raise HTTPException(status_code=503,detail=f"MySQL query failed: {str(e)}. Check DATABASE_URL and run database/schema.sql.")

@app.get("/api/customers")
def customers(limit:int=100, db:Session=Depends(get_db)):
    return [dict(x._mapping) for x in db.execute(text("SELECT * FROM customers ORDER BY created_at DESC LIMIT :n"),{"n":min(limit,500)})]

@app.get("/api/carts")
# def carts(status:str|None=None, limit:int=100, db:Session=Depends(get_db)):
def carts(status: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    sql="SELECT c.*, CONCAT(u.first_name,' ',u.last_name) customer_name FROM carts c JOIN customers u ON u.customer_id=c.customer_id"
    params={"n":min(limit,500)}
    if status:
        sql+=" WHERE c.status=:status"; params["status"]=status
    sql+=" ORDER BY c.last_activity_at DESC LIMIT :n"
    return [dict(x._mapping) for x in db.execute(text(sql),params)]

@app.get("/api/campaigns")
def campaigns(db:Session=Depends(get_db)):
    return [dict(x._mapping) for x in db.execute(text("SELECT * FROM campaigns ORDER BY scheduled_at DESC"))]

# Request model for creating a campaign
class CampaignCreate(BaseModel):
    campaign_name: str
    channel: Literal["EMAIL", "SMS"]
    variant: Literal["A", "B", "C"]
    target_audience: str
    scheduled_at: datetime

# Request model for updating a campaign
class CampaignUpdate(BaseModel):
    campaign_name: Optional[str] = None
    channel: Optional[Literal["EMAIL", "SMS"]] = None
    variant: Optional[Literal["A", "B", "C"]] = None
    target_audience: Optional[str] = None
    scheduled_at: Optional[datetime] = None

# Create a new campaign
@app.post("/api/campaigns")
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db)
):
    try:
        year = campaign.scheduled_at.year
        prefix = f"CMP-{year}-%"

        # Generate the next campaign ID
        result = db.execute(
            text("""
                SELECT COALESCE(
                    MAX(CAST(SUBSTRING(campaign_id, 10) AS UNSIGNED)),
                    0
                )
                FROM campaigns
                WHERE campaign_id LIKE :prefix
            """),
            {"prefix": prefix}
        )

        # next_number = result.scalar() + 1
        next_number = int(result.scalar() or 0) + 1
        
        campaign_id = f"CMP-{year}-{next_number:06d}"

        # Insert campaign into MySQL
        db.execute(
            text("""
                INSERT INTO campaigns (
                    campaign_id,
                    campaign_name,
                    channel,
                    variant,
                    target_audience,
                    scheduled_at,
                    status,
                    created_at
                )
                VALUES (
                    :campaign_id,
                    :campaign_name,
                    :channel,
                    :variant,
                    :target_audience,
                    :scheduled_at,
                    'DRAFT',
                    NOW()
                )
            """),
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign.campaign_name,
                "channel": campaign.channel,
                "variant": campaign.variant,
                "target_audience": campaign.target_audience,
                "scheduled_at": campaign.scheduled_at
            }
        )

        db.commit()

        return {
            "message": "Campaign created successfully",
            "campaign_id": campaign_id,
            "status": "DRAFT"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Campaign creation failed: {str(e)}"
        )
    # Update an existing draft campaign
@app.patch("/api/campaigns/{campaign_id}")
def update_campaign(
    campaign_id: str,
    campaign: CampaignUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Check whether campaign exists
        existing = db.execute(
            text("""
                SELECT campaign_id, status
                FROM campaigns
                WHERE campaign_id = :campaign_id
            """),
            {"campaign_id": campaign_id}
        ).mappings().first()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Campaign not found"
            )

        # Only draft campaigns can be edited
        if existing["status"] != "DRAFT":
            raise HTTPException(
                status_code=400,
                detail="Only DRAFT campaigns can be edited"
            )

        # Get only the fields provided by the user
        updates = campaign.dict(exclude_unset=True)

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        # Build the UPDATE query safely
        allowed_fields = {
            "campaign_name",
            "channel",
            "variant",
            "target_audience",
            "scheduled_at"
        }

        set_clause = ", ".join(
            f"{field} = :{field}"
            for field in updates
            if field in allowed_fields
        )

        updates["campaign_id"] = campaign_id

        db.execute(
            text(f"""
                UPDATE campaigns
                SET {set_clause}
                WHERE campaign_id = :campaign_id
            """),
            updates
        )

        db.commit()

        return {
            "message": "Campaign updated successfully",
            "campaign_id": campaign_id,
            "status": "DRAFT"
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Campaign update failed: {str(e)}"
        )
@app.get("/api/sends")
def sends(limit:int=100, db:Session=Depends(get_db)):
    return [dict(x._mapping) for x in db.execute(text("SELECT * FROM send_attempts ORDER BY attempted_at DESC LIMIT :n"),{"n":min(limit,500)})]

@app.get("/api/send-events")
def get_send_events(
    send_id: str = None,
    event_type: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = """
        SELECT
            event_id,
            send_id,
            event_type,
            event_at,
            provider_event_id,
            event_metadata
        FROM send_events
        WHERE 1=1
    """

    params = {}

    if send_id:
        query += " AND send_id = :send_id"
        params["send_id"] = send_id

    if event_type:
        query += " AND event_type = :event_type"
        params["event_type"] = event_type.upper()

    query += " ORDER BY event_at DESC LIMIT :limit"
    params["limit"] = min(max(limit, 1), 500)

    rows = db.execute(text(query), params)

    return [dict(row._mapping) for row in rows]

# @app.get("/api/orders")
# def orders(limit:int=100, db:Session=Depends(get_db)):
#     return [dict(x._mapping) for x in db.execute(text("SELECT o.*,a.campaign_id,a.attributed_revenue FROM orders o LEFT JOIN attributions a ON a.order_id=o.order_id ORDER BY ordered_at DESC LIMIT :n"),{"n":min(limit,500)})]

@app.get("/api/orders")
def orders(limit: int = 100, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            o.*,
            a.attribution_id,
            a.campaign_id AS attributed_campaign_id,
            a.send_id AS attributed_send_id,
            a.model AS attribution_model,
            a.attributed_at,
            a.attributed_revenue,
            a.reason AS attribution_reason
        FROM orders o
        LEFT JOIN attributions a
            ON a.order_id = o.order_id
        ORDER BY o.ordered_at DESC
        LIMIT :n
    """)

    result = db.execute(
        query,
        {"n": min(max(limit, 1), 500)}
    )

    return [dict(row._mapping) for row in result]
@app.get("/api/anomalies")
def anomalies(db:Session=Depends(get_db)):
    try: return [dict(x._mapping) for x in db.execute(text("SELECT * FROM anomaly_issues ORDER BY detected_at DESC"))]
    except Exception: return []

@app.get("/api/consents")
def all_consents(limit: int = 1000, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            c.consent_id,
            c.customer_id,
            CONCAT(cu.first_name, ' ', cu.last_name) AS customer_name,
            c.channel,
            c.status,
            c.effective_at,
            c.withdrawn_at,
            c.source,
            c.created_at
        FROM consents c
        LEFT JOIN customers cu
            ON c.customer_id = cu.customer_id
        ORDER BY c.effective_at DESC
        LIMIT :limit
    """)

    result = db.execute(query, {"limit": min(max(limit, 1), 5000)})
    return [dict(row._mapping) for row in result]

@app.get("/api/consent/{customer_id}")
def consent(customer_id:str, db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT * FROM consents WHERE customer_id=:id ORDER BY effective_at DESC"),{"id":customer_id})
    return [dict(x._mapping) for x in rows]

@app.get("/api/audit-decisions")
def audit_decisions(limit: int = 200, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            decision_id,
            customer_id,
            cart_id,
            channel,
            decision,
            reason_code,
            detail,
            decided_at
        FROM audit_decisions
        ORDER BY decided_at DESC
        LIMIT :n
    """)

    result = db.execute(query, {"n": min(max(limit, 1), 500)})
    return [dict(row._mapping) for row in result]


# Campaign orchestration routes
from .api.orchestration import router as orchestration_router

app.include_router(orchestration_router)
