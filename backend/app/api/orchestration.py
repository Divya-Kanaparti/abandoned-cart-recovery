
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.campaign_orchestrator import run_recovery_workflow


router = APIRouter(
    prefix="/api/orchestration",
    tags=["Campaign Orchestration"]
)


class WorkflowRequest(BaseModel):
    campaign_id: str
    limit: int = Field(default=500, ge=1, le=5000)
    dry_run: bool = True
    abandonment_minutes: int = Field(default=60, ge=1, le=10080)


@router.post("/run")
def execute_recovery(
    request: WorkflowRequest,
    db: Session = Depends(get_db)
):
    
    try:
        result = run_recovery_workflow(
            db=db,
            campaign_id=request.campaign_id,
            now=datetime.now(),
            limit=request.limit,
            dry_run=request.dry_run,
            abandonment_minutes=request.abandonment_minutes
        )

        if request.dry_run:
            # Roll back all temporary database changes.
            db.rollback()
        else:
            # Persist actual workflow changes.
            db.commit()

        return {
            "status": "success",
            "message": (
                "Workflow preview completed"
                if request.dry_run
                else "Recovery workflow executed"
            ),
            "result": result
        }

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(exc)}"
        )

    