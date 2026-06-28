"""
Dataset API Routes
Endpoints for uploading, listing, retrieving, and setting targets on datasets.
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload CSV dataset and perform automated type/summary analysis."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        content = await file.read()
        dataset_meta = DatasetService.upload_dataset(content, file.filename, db)
        return dataset_meta
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    """Retrieve list of all uploaded datasets."""
    datasets = DatasetService.get_all_datasets(db)
    return [
        {
            "id": d.id,
            "name": d.name,
            "filename": d.filename,
            "rows": d.rows,
            "columns": d.columns,
            "numerical_columns": d.numerical_columns,
            "categorical_columns": d.categorical_columns,
            "target_column": d.target_column,
            "upload_date": d.upload_date.isoformat(),
            "status": d.status,
            "summary": d.summary
        }
        for d in datasets
    ]

@router.get("/{dataset_id}")
def get_dataset_by_id(dataset_id: int, db: Session = Depends(get_db)):
    """Retrieve full metadata for a specific dataset."""
    d = DatasetService.get_dataset(dataset_id, db)
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": d.id,
        "name": d.name,
        "filename": d.filename,
        "rows": d.rows,
        "columns": d.columns,
        "numerical_columns": d.numerical_columns,
        "categorical_columns": d.categorical_columns,
        "target_column": d.target_column,
        "upload_date": d.upload_date.isoformat(),
        "status": d.status,
        "summary": d.summary,
        "column_types": d.column_types
    }

@router.get("/{dataset_id}/preview")
def get_preview(
    dataset_id: int,
    rows: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve the first N rows of the dataset for rendering in UI."""
    try:
        preview = DatasetService.get_dataset_preview(dataset_id, db, rows)
        return preview
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{dataset_id}/target")
def set_target_column(
    dataset_id: int,
    target_column: str,
    db: Session = Depends(get_db)
):
    """Update or specify the default target column for the dataset."""
    try:
        res = DatasetService.update_target_column(dataset_id, target_column, db)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{dataset_id}")
def delete_dataset_by_id(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset and its associated files."""
    success = DatasetService.delete_dataset(dataset_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"message": f"Dataset {dataset_id} deleted successfully."}
