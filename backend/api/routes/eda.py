"""
EDA API Routes
Runs the EDA engine on a dataset and retrieves results.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.dataset_service import DatasetService
from services.eda_service import EDAService

router = APIRouter(prefix="/eda", tags=["EDA"])

@router.post("/{dataset_id}")
def run_eda(dataset_id: int, db: Session = Depends(get_db)):
    """Run full automated EDA pipeline on the dataset."""
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = DatasetService.load_dataframe(dataset)
        eda_results = EDAService.run_full_eda(df, dataset.target_column)

        # Update dataset status in DB
        dataset.status = "analyzed"
        db.commit()

        return eda_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run EDA: {str(e)}")
