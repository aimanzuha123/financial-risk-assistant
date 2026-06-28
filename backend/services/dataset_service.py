"""
Dataset Service
Handles CSV upload, parsing, column detection, and dataset management.
"""
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from config.settings import settings
from database.models import Dataset
from utils.helpers import detect_column_types, calculate_data_hash, safe_json_serialize


class DatasetService:
    """Service for dataset upload, validation, and management."""

    @staticmethod
    def upload_dataset(file_content: bytes, filename: str, db: Session) -> Dict:
        """
        Upload and process a CSV file.

        Steps:
        1. Save file to disk
        2. Parse CSV with pandas
        3. Detect column types
        4. Store metadata in database
        """
        # Save file
        file_path = settings.UPLOAD_DIR / filename
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Parse CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            os.remove(file_path)
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        if df.empty:
            os.remove(file_path)
            raise ValueError("CSV file is empty.")

        # Detect column types
        col_info = detect_column_types(df)

        # Build summary statistics
        summary = DatasetService._build_summary(df)

        # Create database record
        dataset = Dataset(
            name=filename.rsplit(".", 1)[0],
            filename=filename,
            file_path=str(file_path),
            rows=len(df),
            columns=len(df.columns),
            numerical_columns=col_info["numerical"],
            categorical_columns=col_info["categorical"],
            target_column=col_info["target_column"],
            column_types=safe_json_serialize({
                col: str(dtype) for col, dtype in df.dtypes.items()
            }),
            summary=safe_json_serialize(summary),
            status="uploaded",
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return {
            "id": dataset.id,
            "name": dataset.name,
            "filename": dataset.filename,
            "rows": dataset.rows,
            "columns": dataset.columns,
            "numerical_columns": col_info["numerical"],
            "categorical_columns": col_info["categorical"],
            "target_column": col_info["target_column"],
            "target_candidates": col_info["target_candidates"],
            "column_types": dataset.column_types,
            "summary": summary,
            "status": "uploaded",
        }

    @staticmethod
    def _build_summary(df: pd.DataFrame) -> Dict:
        """Build comprehensive dataset summary statistics."""
        summary = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            "missing_values": safe_json_serialize(df.isnull().sum().to_dict()),
            "missing_percentage": safe_json_serialize(
                (df.isnull().sum() / len(df) * 100).round(2).to_dict()
            ),
            "duplicates": int(df.duplicated().sum()),
            "duplicate_percentage": round(df.duplicated().sum() / len(df) * 100, 2),
        }

        # Numerical stats
        numerical_cols = df.select_dtypes(include=["number"]).columns
        if len(numerical_cols) > 0:
            desc = df[numerical_cols].describe().round(4)
            summary["numerical_stats"] = safe_json_serialize(desc.to_dict())

        # Categorical stats
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if len(cat_cols) > 0:
            cat_stats = {}
            for col in cat_cols:
                cat_stats[col] = {
                    "unique": int(df[col].nunique()),
                    "top": str(df[col].mode().iloc[0]) if not df[col].mode().empty else "N/A",
                    "freq": int(df[col].value_counts().iloc[0]) if not df[col].value_counts().empty else 0,
                    "value_counts": safe_json_serialize(
                        df[col].value_counts().head(10).to_dict()
                    ),
                }
            summary["categorical_stats"] = cat_stats

        return summary

    @staticmethod
    def get_dataset(dataset_id: int, db: Session) -> Optional[Dataset]:
        """Retrieve a dataset by ID."""
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def get_all_datasets(db: Session):
        """Retrieve all datasets ordered by upload date."""
        return db.query(Dataset).order_by(Dataset.upload_date.desc()).all()

    @staticmethod
    def load_dataframe(dataset: Dataset) -> pd.DataFrame:
        """Load the CSV file into a pandas DataFrame."""
        return pd.read_csv(dataset.file_path)

    @staticmethod
    def update_target_column(dataset_id: int, target_column: str, db: Session) -> Dict:
        """Update the target column for a dataset."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        dataset.target_column = target_column
        db.commit()
        db.refresh(dataset)

        return {
            "id": dataset.id,
            "target_column": dataset.target_column,
            "status": "updated",
        }

    @staticmethod
    def delete_dataset(dataset_id: int, db: Session) -> bool:
        """Delete a dataset and its file."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return False

        # Remove file
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)

        db.delete(dataset)
        db.commit()
        return True

    @staticmethod
    def get_dataset_preview(dataset_id: int, db: Session, rows: int = 20) -> Dict:
        """Get a preview of the dataset (first N rows)."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        df = pd.read_csv(dataset.file_path)
        preview = df.head(rows)

        return {
            "columns": list(preview.columns),
            "data": safe_json_serialize(preview.to_dict(orient="records")),
            "total_rows": len(df),
            "preview_rows": len(preview),
        }
