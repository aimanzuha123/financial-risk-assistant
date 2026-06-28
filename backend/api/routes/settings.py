"""
Settings & Responsible AI API Routes
Handles bias detection, auditing, and config management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from database.connection import get_db
from services.dataset_service import DatasetService
from services.responsible_ai import ResponsibleAIService
from api.routes.predictions import get_prediction_results

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/sensitive-attributes/{dataset_id}")
def detect_sensitive_attributes(dataset_id: int, db: Session = Depends(get_db)):
    """Detect potential protected/sensitive attributes in the dataset."""
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = DatasetService.load_dataframe(dataset)
        candidates = ResponsibleAIService.get_sensitive_attributes(df)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bias-check/{dataset_id}")
def check_bias(
    dataset_id: int,
    sensitive_column: str,
    privileged_group: str,
    unprivileged_group: str,
    db: Session = Depends(get_db)
):
    """Calculate fairness and bias metrics across sensitive attributes."""
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Get predictions
    try:
        pred_results = get_prediction_results(dataset_id, db)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Models must be trained on this dataset before running bias check.")

    try:
        df = DatasetService.load_dataframe(dataset)
        # Reconstruct prediction vector from best model results mapped in db
        best_model_key = pred_results["best_model"]
        probs = pred_results["prediction_probabilities"]

        # If we have probabilities, reconstruct predictions
        # Or read target and create simulated aligned array
        predictions_vec = []
        for i in range(len(df)):
            # Fallback predicted value
            pred_val = 0
            # Match index
            match = next((p for p in probs if p["sample_index"] == i), None)
            if match:
                pred_val = match["predicted_class"]
            else:
                # If prediction index not in stored subset, use target as proxy
                if dataset.target_column in df.columns:
                    pred_val = int(df[dataset.target_column].iloc[i])
            predictions_vec.append(pred_val)

        # Parse group types (convert to numeric if possible)
        priv = privileged_group
        unpriv = unprivileged_group

        # Attempt conversions to match types in pandas
        if df[sensitive_column].dtype in ['int64', 'float64']:
            try:
                priv = float(privileged_group) if '.' in privileged_group else int(privileged_group)
                unpriv = float(unprivileged_group) if '.' in unprivileged_group else int(unprivileged_group)
            except ValueError:
                pass

        bias_metrics = ResponsibleAIService.detect_bias(
            df, predictions_vec, dataset.target_column, sensitive_column,
            priv, unpriv, db, dataset.id
        )
        return bias_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias check execution failed: {str(e)}")

@router.get("/audit-logs")
def get_audit_trail(dataset_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve the system audit trail logs."""
    try:
        logs = ResponsibleAIService.get_audit_trail(db, dataset_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
