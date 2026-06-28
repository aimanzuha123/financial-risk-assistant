"""
Collections API Routes
Handles collections strategy recommendations, human approval pipelines, and agentic updates.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from services.dataset_service import DatasetService
from services.collections_service import CollectionsService
from api.routes.predictions import get_prediction_results

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.post("/{dataset_id}/generate")
def generate_collections(dataset_id: int, db: Session = Depends(get_db)):
    """Generate default collections strategy recommendations for the entire portfolio."""
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = DatasetService.load_dataframe(dataset)

        # Get optional ML predictions to enhance strategy
        pred_results = None
        try:
            pred_results = get_prediction_results(dataset_id, db)
        except HTTPException:
            pass

        actions = CollectionsService.generate_collections_strategy(
            df, dataset.id, pred_results, db
        )
        return actions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate strategy: {str(e)}")

@router.get("/{dataset_id}/actions")
def get_collections_actions(dataset_id: int, db: Session = Depends(get_db)):
    """Retrieve existing collections strategy actions."""
    actions = CollectionsService.get_actions(dataset_id, db)
    return [
        {
            "id": a.id,
            "customer_id": a.customer_id,
            "risk_level": a.risk_level,
            "risk_score": a.risk_score,
            "recommended_action": a.recommended_action,
            "action_details": a.action_details,
            "priority": a.priority,
            "status": a.status,
            "requires_approval": a.requires_human_approval,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat()
        }
        for a in actions
    ]

@router.post("/actions/{action_id}/approve")
def approve_action(
    action_id: int,
    approved_by: str = Query("system_user"),
    db: Session = Depends(get_db)
):
    """Approve a collection action that requires human review."""
    try:
        action = CollectionsService.approve_action(action_id, approved_by, db)
        return {
            "id": action.id,
            "customer_id": action.customer_id,
            "status": action.status,
            "recommended_action": action.recommended_action
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{action_id}/feedback")
def submit_agentic_feedback(
    action_id: int,
    payment_amount: float = Body(0.0, embed=True),
    promise_to_pay: bool = Body(False, embed=True),
    notes: str = Body("", embed=True),
    db: Session = Depends(get_db)
):
    """
    Trigger the Agentic AI feedback loop.
    Updates customer details, recalculates risk score/level, and sets next best action.
    """
    try:
        updated_strategy = CollectionsService.process_agentic_feedback(
            action_id, payment_amount, promise_to_pay, notes, db
        )
        return updated_strategy
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
