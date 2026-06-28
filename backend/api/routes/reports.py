"""
Reports API Routes
Handles executive report generation and downloads PDF files.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from services.dataset_service import DatasetService
from services.eda_service import EDAService
from services.report_service import ReportService
from api.routes.predictions import get_prediction_results

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/{dataset_id}/generate")
def generate_report(dataset_id: int, db: Session = Depends(get_db)):
    """Generate business report data and export to PDF."""
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = DatasetService.load_dataframe(dataset)
        eda_results = EDAService.run_full_eda(df, dataset.target_column)

        # Optional prediction results
        pred_results = None
        try:
            pred_results = get_prediction_results(dataset_id, db)
        except HTTPException:
            pass

        report = ReportService.generate_report(
            df, eda_results, pred_results, dataset.name, dataset.id
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/{dataset_id}/download")
def download_pdf(pdf_path: str):
    """Download the generated PDF report."""
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF report file not found on disk")
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
