"""
Responsible AI Service
Handles fairness metrics, bias detection across sensitive/protected attributes,
explainability generation, audit trail management, data masking for privacy.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from database.models import AuditLog, Dataset
from utils.helpers import safe_json_serialize

class ResponsibleAIService:
    """Implements Responsible AI guidelines: Fairness, Bias, Privacy, Audit, Explainability."""

    @staticmethod
    def detect_bias(
        df: pd.DataFrame,
        predictions: List[int],
        target_col: str,
        sensitive_col: str,
        privileged_group: Any,
        unprivileged_group: Any,
        db: Optional[Session] = None,
        dataset_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate predictive model fairness across protected groups.
        Calculates:
        - Disparate Impact Ratio (DIR) - target: 0.8 to 1.25
        - Statistical Parity Difference (SPD) - target: near 0.0
        - Equal Opportunity Difference (EOD) - target: near 0.0
        """
        if sensitive_col not in df.columns:
            return {"error": f"Sensitive attribute '{sensitive_col}' not found in dataset."}

        # Align lengths
        if len(predictions) != len(df):
            return {"error": "Predictions list length does not match DataFrame rows."}

        # Create localized analysis DataFrame
        analysis_df = pd.DataFrame({
            "sensitive": df[sensitive_col].values,
            "target": df[target_col].values if target_col in df.columns else None,
            "pred": predictions
        })

        # Drop rows with missing values in key columns
        analysis_df = analysis_df.dropna(subset=["sensitive", "pred"])

        # Protected group masks
        is_privileged = analysis_df["sensitive"] == privileged_group
        is_unprivileged = analysis_df["sensitive"] == unprivileged_group

        n_priv = is_privileged.sum()
        n_unpriv = is_unprivileged.sum()

        if n_priv == 0 or n_unpriv == 0:
            return {
                "error": "One or both groups have 0 samples. Verify values.",
                "privileged_count": int(n_priv),
                "unprivileged_count": int(n_unpriv)
            }

        # 1. Selection Rates (Adverse selection rate - positive outcome is predicted low-risk [0])
        # Note: In collections/risk, 0 = low risk (favorable), 1 = default/high-risk (unfavorable).
        # Favorable outcome: pred == 0
        fav_priv = (analysis_df[is_privileged]["pred"] == 0).sum()
        fav_unpriv = (analysis_df[is_unprivileged]["pred"] == 0).sum()

        rate_priv = fav_priv / n_priv
        rate_unpriv = fav_unpriv / n_unpriv

        # Disparate Impact Ratio (DIR)
        dir_val = rate_unpriv / rate_priv if rate_priv > 0 else 0.0

        # Statistical Parity Difference (SPD)
        spd_val = rate_unpriv - rate_priv

        # 2. Equal Opportunity (Requires target label for True Positive Rates)
        eod_val = 0.0
        tpr_priv = 0.0
        tpr_unpriv = 0.0

        if "target" in analysis_df.columns and analysis_df["target"].notna().any():
            # In collections, true default (target=1) is undesirable.
            # True Positive Rate is P(pred=1 | actual=1)
            actual_pos_priv = (analysis_df[is_privileged]["target"] == 1).sum()
            actual_pos_unpriv = (analysis_df[is_unprivileged]["target"] == 1).sum()

            tp_priv = ((analysis_df[is_privileged]["target"] == 1) & (analysis_df[is_privileged]["pred"] == 1)).sum()
            tp_unpriv = ((analysis_df[is_unprivileged]["target"] == 1) & (analysis_df[is_unprivileged]["pred"] == 1)).sum()

            tpr_priv = tp_priv / actual_pos_priv if actual_pos_priv > 0 else 0.0
            tpr_unpriv = tp_unpriv / actual_pos_unpriv if actual_pos_unpriv > 0 else 0.0

            # Equal Opportunity Difference (EOD)
            eod_val = tpr_unpriv - tpr_priv

        # Flag bias
        has_bias = not (0.8 <= dir_val <= 1.25)

        metrics = {
            "sensitive_attribute": sensitive_col,
            "privileged_group": str(privileged_group),
            "unprivileged_group": str(unprivileged_group),
            "privileged_count": int(n_priv),
            "unprivileged_count": int(n_unpriv),
            "favorable_rate_privileged": round(float(rate_priv), 4),
            "favorable_rate_unprivileged": round(float(rate_unpriv), 4),
            "disparate_impact_ratio": round(float(dir_val), 4),
            "statistical_parity_difference": round(float(spd_val), 4),
            "equal_opportunity_difference": round(float(eod_val), 4),
            "has_bias": bool(has_bias),
            "status": "biased" if has_bias else "fair",
            "interpretation": (
                "Biased outcome detected: Disparate Impact Ratio is outside [0.8, 1.25] threshold."
                if has_bias
                else "Fair prediction output: Metrics fall within compliant thresholds."
            )
        }

        # Write responsible AI audit log
        if db and dataset_id:
            audit = AuditLog(
                dataset_id=dataset_id,
                action="Fairness and Bias Verification",
                category="fairness",
                details=safe_json_serialize(metrics),
                severity="warning" if has_bias else "info"
            )
            db.add(audit)
            db.commit()

        return safe_json_serialize(metrics)

    @staticmethod
    def get_sensitive_attributes(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify candidate columns that might represent sensitive attributes."""
        sensitive_keywords = [
            "age", "gender", "sex", "race", "ethnicity", "religion",
            "marital", "status", "zip", "postal", "location"
        ]
        candidates = []
        for col in df.columns:
            for kw in sensitive_keywords:
                if kw in col.lower():
                    unique_vals = df[col].dropna().unique().tolist()
                    candidates.append({
                        "column": col,
                        "unique_values": unique_vals[:10]  # Limit preview
                    })
                    break
        return candidates

    @staticmethod
    def get_audit_trail(db: Session, dataset_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve system audits."""
        query = db.query(AuditLog)
        if dataset_id:
            query = query.filter(AuditLog.dataset_id == dataset_id)
        logs = query.order_by(AuditLog.timestamp.desc()).all()

        return [
            {
                "id": log.id,
                "dataset_id": log.dataset_id,
                "action": log.action,
                "category": log.category,
                "details": log.details,
                "user": log.user,
                "timestamp": log.timestamp.isoformat(),
                "severity": log.severity
            }
            for log in logs
        ]

    @staticmethod
    def log_manual_intervention(
        dataset_id: int,
        action: str,
        user: str,
        details: Dict[str, Any],
        db: Session
    ) -> AuditLog:
        """Create manual override or compliance review audit event."""
        log = AuditLog(
            dataset_id=dataset_id,
            action=action,
            category="approval",
            details=safe_json_serialize(details),
            user=user,
            severity="info"
        )
        db.add(log)
        db.commit()
        return log
