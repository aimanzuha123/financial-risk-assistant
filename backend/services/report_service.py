"""
Report Service
Generates comprehensive executive business reports with AI-powered insights,
risk analysis, customer segmentation, and actionable recommendations.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd

from config.settings import settings
from utils.helpers import safe_json_serialize
from utils.pdf_generator import PDFReportGenerator


class ReportService:
    """Service for generating executive business reports."""

    @staticmethod
    def generate_report(
        df: pd.DataFrame,
        eda_results: Dict,
        prediction_results: Optional[Dict],
        dataset_name: str,
        dataset_id: int,
    ) -> Dict:
        """
        Generate a complete executive business report.

        Returns report data and the path to the generated PDF.
        """
        report_data = {
            "dataset_name": dataset_name,
            "total_records": len(df),
            "generated_at": datetime.now().isoformat(),
        }

        # 1. Executive Summary
        report_data["executive_summary"] = ReportService._executive_summary(
            df, eda_results, prediction_results
        )

        # 2. Business Insights
        report_data["business_insights"] = ReportService._business_insights(
            df, eda_results
        )

        # 3. Risk Trends
        report_data["risk_trends"] = ReportService._risk_trends(df, eda_results)

        # 4. Customer Segmentation
        report_data["customer_segmentation"] = ReportService._customer_segmentation(df)

        # 5. Recommendations
        report_data["recommendations"] = ReportService._recommendations(
            df, eda_results, prediction_results
        )

        # 6. Financial Impact
        report_data["financial_impact"] = ReportService._financial_impact(
            df, eda_results, prediction_results
        )

        # 7. Intervention Strategy
        report_data["intervention_strategy"] = ReportService._intervention_strategy(
            df, prediction_results
        )

        # 8. Next Steps
        report_data["next_steps"] = ReportService._next_steps(prediction_results)

        # 9. Model Performance (if predictions exist)
        if prediction_results and "best_model" in prediction_results:
            best_key = prediction_results["best_model"]
            best_model = prediction_results["models"][best_key]
            report_data["model_performance"] = {
                "model_name": best_model["model_name"],
                **best_model["metrics"],
            }

        # Generate PDF
        pdf_filename = f"report_{dataset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = str(settings.REPORTS_DIR / pdf_filename)

        try:
            generator = PDFReportGenerator()
            generator.generate_report(report_data, pdf_path)
            report_data["pdf_path"] = pdf_path
            report_data["pdf_filename"] = pdf_filename
        except Exception as e:
            report_data["pdf_error"] = str(e)

        return safe_json_serialize(report_data)

    @staticmethod
    def _executive_summary(
        df: pd.DataFrame,
        eda_results: Dict,
        prediction_results: Optional[Dict],
    ) -> str:
        """Generate an executive summary paragraph."""
        n_rows = len(df)
        n_cols = len(df.columns)
        summary = eda_results.get("summary", {})
        missing = eda_results.get("missing_values", {})
        risk = eda_results.get("risk_profile", {})

        lines = [
            f"This report presents a comprehensive analysis of {n_rows:,} records "
            f"across {n_cols} attributes in the {df.columns[0] if len(df.columns) > 0 else 'N/A'} dataset.",
            "",
            f"Data Quality: The dataset contains {missing.get('total_missing', 0):,} missing values "
            f"across {missing.get('columns_with_missing', 0)} columns. "
            f"{eda_results.get('duplicates', {}).get('total_duplicates', 0)} duplicate records were identified.",
        ]

        if risk and "target_distribution" in risk:
            dist = risk["target_distribution"]
            lines.append("")
            lines.append("Risk Distribution:")
            for label, info in dist.items():
                lines.append(
                    f"  - Class {label}: {info.get('count', 0):,} records "
                    f"({info.get('percentage', 0):.1f}%)"
                )

        if prediction_results and "best_model_name" in prediction_results:
            lines.append("")
            lines.append(
                f"Best Performing Model: {prediction_results['best_model_name']} "
                f"(F1 Score: {prediction_results.get('best_score', 0):.4f})"
            )

        return "\n".join(lines)

    @staticmethod
    def _business_insights(df: pd.DataFrame, eda_results: Dict) -> str:
        """Generate business insights section."""
        insights = eda_results.get("business_insights", [])
        if isinstance(insights, list):
            return "\n\n".join(insights)
        return str(insights)

    @staticmethod
    def _risk_trends(df: pd.DataFrame, eda_results: Dict) -> Dict:
        """Analyze risk trends from the data."""
        risk = eda_results.get("risk_profile", {})
        outliers = eda_results.get("outliers", {})

        trends = {
            "risk_distribution": risk.get("target_distribution", {}),
            "class_imbalance": risk.get("is_imbalanced", False),
            "imbalance_ratio": risk.get("risk_ratio", 0),
            "features_with_outliers": outliers.get("total_columns_with_outliers", 0),
        }

        # Add correlation insights
        corr = eda_results.get("correlation", {})
        strong = corr.get("strong_correlations", [])
        if strong:
            trends["key_correlations"] = [
                f"{c['feature_1']} ↔ {c['feature_2']}: {c['correlation']:.3f}"
                for c in strong[:5]
            ]

        return trends

    @staticmethod
    def _customer_segmentation(df: pd.DataFrame) -> List[Dict]:
        """Perform basic customer segmentation using quartiles."""
        numerical = df.select_dtypes(include=["number"])
        if numerical.shape[1] == 0:
            return []

        # Use first meaningful numerical column for segmentation
        segments = []
        segment_col = numerical.columns[0]

        try:
            quartiles = pd.qcut(numerical[segment_col], q=4, labels=["Low", "Medium-Low", "Medium-High", "High"], duplicates="drop")
            for label in quartiles.unique():
                mask = quartiles == label
                segment_data = numerical[mask]
                segments.append({
                    "segment": str(label),
                    "count": int(mask.sum()),
                    "percentage": round(float(mask.sum() / len(df) * 100), 1),
                    "avg_value": round(float(segment_data[segment_col].mean()), 2),
                })
        except Exception:
            # Fallback: simple binary segmentation
            median = numerical[segment_col].median()
            above = (numerical[segment_col] >= median).sum()
            below = (numerical[segment_col] < median).sum()
            segments = [
                {"segment": "Above Median", "count": int(above),
                 "percentage": round(float(above / len(df) * 100), 1)},
                {"segment": "Below Median", "count": int(below),
                 "percentage": round(float(below / len(df) * 100), 1)},
            ]

        return segments

    @staticmethod
    def _recommendations(
        df: pd.DataFrame,
        eda_results: Dict,
        prediction_results: Optional[Dict],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        # Data quality recommendations
        missing = eda_results.get("missing_values", {})
        if missing.get("total_missing", 0) > 0:
            recs.append(
                "Implement automated data quality checks to address "
                f"{missing['total_missing']:,} missing values across "
                f"{missing.get('columns_with_missing', 0)} columns."
            )

        dups = eda_results.get("duplicates", {}).get("total_duplicates", 0)
        if dups > 0:
            recs.append(
                f"Deduplicate {dups:,} duplicate records to improve "
                "data integrity and model performance."
            )

        # Risk recommendations
        risk = eda_results.get("risk_profile", {})
        if risk.get("is_imbalanced"):
            recs.append(
                "Address class imbalance through oversampling (SMOTE), "
                "undersampling, or cost-sensitive learning to improve "
                "minority class detection."
            )

        # Model recommendations
        if prediction_results:
            best_f1 = prediction_results.get("best_score", 0)
            if best_f1 < 0.7:
                recs.append(
                    "Model performance is below target. Consider "
                    "feature engineering, hyperparameter tuning, or "
                    "ensemble methods to improve prediction accuracy."
                )
            recs.append(
                "Deploy the best-performing model with A/B testing to "
                "validate real-world performance before full rollout."
            )

        # General recommendations
        recs.extend([
            "Establish continuous monitoring dashboards for key risk indicators.",
            "Implement early warning systems for customers approaching delinquency thresholds.",
            "Create automated intervention workflows triggered by risk score changes.",
            "Schedule quarterly model retraining to account for distribution drift.",
        ])

        return recs

    @staticmethod
    def _financial_impact(
        df: pd.DataFrame,
        eda_results: Dict,
        prediction_results: Optional[Dict],
    ) -> str:
        """Estimate financial impact of findings."""
        lines = []

        risk = eda_results.get("risk_profile", {})
        dist = risk.get("target_distribution", {})

        # Estimate high-risk population
        for label, info in dist.items():
            if "1" in str(label) or "yes" in str(label).lower() or "default" in str(label).lower():
                pct = info.get("percentage", 0)
                count = info.get("count", 0)
                lines.append(
                    f"High-risk segment represents {pct:.1f}% of the portfolio "
                    f"({count:,} accounts)."
                )
                lines.append(
                    f"Proactive intervention for these accounts could reduce "
                    f"delinquency by an estimated 15-25% based on industry benchmarks."
                )
                lines.append(
                    f"Assuming an average account value of $5,000, potential "
                    f"savings range from ${count * 5000 * 0.15:,.0f} to "
                    f"${count * 5000 * 0.25:,.0f}."
                )
                break

        if prediction_results:
            best = prediction_results.get("best_score", 0)
            lines.append(
                f"\nModel achieves {best * 100:.1f}% F1 score, enabling "
                f"accurate identification of at-risk customers before default."
            )

        if not lines:
            lines.append(
                "Financial impact analysis requires target variable classification. "
                "Configure the target column to enable impact estimation."
            )

        return "\n".join(lines)

    @staticmethod
    def _intervention_strategy(
        df: pd.DataFrame, prediction_results: Optional[Dict]
    ) -> List[str]:
        """Generate intervention strategy recommendations."""
        return [
            "Tier 1 (Low Risk): Automated email reminders with payment links. "
            "Send at 7, 14, and 21 days past due.",
            "Tier 2 (Medium Risk): Personalized SMS campaigns with payment plan options. "
            "Deploy at 15 days past due with escalation at 30 days.",
            "Tier 3 (High Risk): Direct phone contact by trained agents. "
            "Initiate within 10 days and offer hardship programs.",
            "Tier 4 (Critical Risk): Escalate to senior collections or legal review. "
            "Requires human approval before action.",
            "Implement feedback loops: Every resolved case feeds back into the "
            "ML model for continuous improvement.",
            "A/B test intervention channels (email vs SMS vs phone) to optimize "
            "recovery rates by customer segment.",
        ]

    @staticmethod
    def _next_steps(prediction_results: Optional[Dict]) -> List[str]:
        """Generate next steps for stakeholders."""
        steps = [
            "Review and approve the AI-generated risk classifications.",
            "Deploy automated collection workflows for Tier 1 and Tier 2 customers.",
            "Train collections team on AI-assisted decision support tools.",
            "Establish monthly model performance review cadence.",
            "Integrate real-time payment data feeds for dynamic risk scoring.",
            "Implement responsible AI monitoring for bias and fairness.",
            "Schedule stakeholder presentation to review findings and approve strategy.",
        ]
        return steps
