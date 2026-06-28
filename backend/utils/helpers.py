"""
Utility Helpers
Common utility functions used across the application.
"""
import uuid
import re
import hashlib
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())[:8]


def detect_column_types(df: pd.DataFrame) -> Dict:
    """
    Automatically detect column types in a DataFrame.
    Returns a dictionary with numerical, categorical, datetime, boolean,
    and potential target columns.
    """
    numerical = []
    categorical = []
    datetime_cols = []
    boolean_cols = []
    target_candidates = []

    for col in df.columns:
        # Skip columns with all missing values
        if df[col].isna().all():
            continue

        dtype = df[col].dtype

        # Boolean detection
        unique_vals = df[col].dropna().unique()
        if set(unique_vals).issubset({0, 1, True, False, "Yes", "No", "yes", "no", "Y", "N"}):
            boolean_cols.append(col)
            target_candidates.append(col)
            continue

        # Datetime detection
        if dtype == "datetime64[ns]" or "date" in col.lower() or "time" in col.lower():
            try:
                pd.to_datetime(df[col], errors="raise")
                datetime_cols.append(col)
                continue
            except (ValueError, TypeError):
                pass

        # Numerical detection
        if np.issubdtype(dtype, np.number):
            numerical.append(col)
            # Binary numerical columns are target candidates
            if len(unique_vals) == 2:
                target_candidates.append(col)
        else:
            # Categorical
            n_unique = df[col].nunique()
            if n_unique <= 20 or n_unique / len(df) < 0.05:
                categorical.append(col)
                if n_unique == 2:
                    target_candidates.append(col)
            else:
                categorical.append(col)

    # Auto-detect target column heuristics
    target_column = _detect_target_column(df, target_candidates)

    return {
        "numerical": numerical,
        "categorical": categorical,
        "datetime": datetime_cols,
        "boolean": boolean_cols,
        "target_candidates": target_candidates,
        "target_column": target_column,
    }


def _detect_target_column(df: pd.DataFrame, candidates: List[str]) -> str:
    """
    Heuristic-based target column detection.
    Looks for common names like 'default', 'delinquent', 'risk', 'target', 'label', etc.
    """
    priority_keywords = [
        "default", "delinquent", "delinquency", "risk", "target", "label",
        "churn", "fraud", "is_default", "is_delinquent", "loan_status",
        "credit_risk", "payment_status", "overdue", "late_payment",
        "bad_loan", "status",
    ]

    # First: check candidates against priority keywords
    for keyword in priority_keywords:
        for col in candidates:
            if keyword in col.lower().replace("_", "").replace("-", ""):
                return col

    # Second: check all columns
    for keyword in priority_keywords:
        for col in df.columns:
            if keyword in col.lower().replace("_", "").replace("-", ""):
                unique = df[col].dropna().nunique()
                if unique <= 5:
                    return col

    # Fallback: first binary candidate
    if candidates:
        return candidates[0]

    return ""


def mask_pii(text: str) -> str:
    """
    Mask personally identifiable information in text.
    Handles emails, phone numbers, SSNs, and credit card numbers.
    """
    # Email
    text = re.sub(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[EMAIL_MASKED]",
        text,
    )
    # Phone numbers
    text = re.sub(
        r"\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b",
        "[PHONE_MASKED]",
        text,
    )
    # SSN
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_MASKED]", text)
    # Credit card
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CC_MASKED]", text)

    return text


def calculate_data_hash(df: pd.DataFrame) -> str:
    """Calculate a hash of a DataFrame for data integrity verification."""
    content = pd.util.hash_pandas_object(df).values.tobytes()
    return hashlib.sha256(content).hexdigest()[:16]


def format_percentage(value: float) -> str:
    """Format a float as a percentage string."""
    return f"{value * 100:.2f}%"


def safe_json_serialize(obj) -> object:
    """Convert numpy types to Python natives for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(i) for i in obj]
    return obj
