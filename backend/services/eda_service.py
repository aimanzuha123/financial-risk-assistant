"""
EDA Service
Automated Exploratory Data Analysis engine that generates comprehensive
analysis including missing values, duplicates, outliers, correlations,
distributions, feature importance, risk profiling, and business insights.
"""
import io
import base64
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

from config.settings import settings
from utils.helpers import safe_json_serialize


class EDAService:
    """Comprehensive EDA engine for financial datasets."""

    # Color palette for charts
    COLORS = [
        "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd",
        "#818cf8", "#60a5fa", "#38bdf8", "#22d3ee",
        "#2dd4bf", "#34d399", "#4ade80", "#a3e635",
        "#facc15", "#fb923c", "#f87171", "#e879f9",
    ]

    @staticmethod
    def run_full_eda(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict:
        """
        Run complete EDA pipeline.

        Returns a dictionary containing all analysis results and
        base64-encoded chart images.
        """
        results = {}

        # 1. Dataset Summary
        results["summary"] = EDAService._dataset_summary(df)

        # 2. Missing Values Analysis
        results["missing_values"] = EDAService._missing_values(df)

        # 3. Duplicate Detection
        results["duplicates"] = EDAService._duplicate_detection(df)

        # 4. Outlier Detection
        results["outliers"] = EDAService._outlier_detection(df)

        # 5. Correlation Analysis
        results["correlation"] = EDAService._correlation_analysis(df)

        # 6. Distribution Analysis
        results["distributions"] = EDAService._distribution_analysis(df)

        # 7. Feature Importance (if target exists)
        if target_col and target_col in df.columns:
            results["feature_importance"] = EDAService._feature_importance(df, target_col)

        # 8. Risk Profiling
        if target_col and target_col in df.columns:
            results["risk_profile"] = EDAService._risk_profiling(df, target_col)

        # 9. Charts
        results["charts"] = EDAService._generate_charts(df, target_col)

        # 10. Business Insights
        results["business_insights"] = EDAService._generate_insights(df, target_col, results)

        return safe_json_serialize(results)

    @staticmethod
    def _dataset_summary(df: pd.DataFrame) -> Dict:
        """Generate comprehensive dataset summary."""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2),
            "numerical_columns": list(df.select_dtypes(include=["number"]).columns),
            "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
            "total_missing": int(df.isnull().sum().sum()),
            "total_duplicates": int(df.duplicated().sum()),
            "column_count": {
                "numerical": len(df.select_dtypes(include=["number"]).columns),
                "categorical": len(df.select_dtypes(include=["object", "category"]).columns),
                "total": len(df.columns),
            },
        }

    @staticmethod
    def _missing_values(df: pd.DataFrame) -> Dict:
        """Analyze missing values across all columns."""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)

        return {
            "total_missing": int(missing.sum()),
            "columns_with_missing": int((missing > 0).sum()),
            "details": {
                col: {
                    "count": int(missing[col]),
                    "percentage": float(missing_pct[col]),
                }
                for col in df.columns
                if missing[col] > 0
            },
            "strategy_recommendations": EDAService._missing_value_strategies(df, missing),
        }

    @staticmethod
    def _missing_value_strategies(df: pd.DataFrame, missing: pd.Series) -> List[Dict]:
        """Recommend strategies for handling missing values."""
        strategies = []
        for col in df.columns:
            if missing[col] == 0:
                continue

            pct = missing[col] / len(df) * 100

            if pct > 50:
                strategy = "Consider dropping this column (>50% missing)"
            elif pct > 20:
                strategy = "Use advanced imputation (KNN, iterative)"
            elif np.issubdtype(df[col].dtype, np.number):
                skew = df[col].skew()
                if abs(skew) > 1:
                    strategy = "Impute with median (skewed distribution)"
                else:
                    strategy = "Impute with mean (normal distribution)"
            else:
                strategy = "Impute with mode (most frequent)"

            strategies.append({
                "column": col,
                "missing_pct": round(pct, 2),
                "strategy": strategy,
            })

        return strategies

    @staticmethod
    def _duplicate_detection(df: pd.DataFrame) -> Dict:
        """Detect and analyze duplicate records."""
        n_duplicates = int(df.duplicated().sum())
        return {
            "total_duplicates": n_duplicates,
            "duplicate_percentage": round(n_duplicates / len(df) * 100, 2),
            "recommendation": (
                "No duplicates found — data is clean."
                if n_duplicates == 0
                else f"Found {n_duplicates} duplicates ({n_duplicates / len(df) * 100:.1f}%). "
                     f"Consider removing to prevent model bias."
            ),
        }

    @staticmethod
    def _outlier_detection(df: pd.DataFrame) -> Dict:
        """Detect outliers using IQR and Z-score methods for numerical columns."""
        numerical_cols = df.select_dtypes(include=["number"]).columns
        outlier_report = {}

        for col in numerical_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            # IQR method
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            iqr_outliers = int(((col_data < lower) | (col_data > upper)).sum())

            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            z_outliers = int((z_scores > 3).sum())

            if iqr_outliers > 0 or z_outliers > 0:
                outlier_report[col] = {
                    "iqr_outliers": iqr_outliers,
                    "iqr_percentage": round(iqr_outliers / len(col_data) * 100, 2),
                    "zscore_outliers": z_outliers,
                    "zscore_percentage": round(z_outliers / len(col_data) * 100, 2),
                    "bounds": {
                        "lower": round(float(lower), 4),
                        "upper": round(float(upper), 4),
                    },
                    "stats": {
                        "mean": round(float(col_data.mean()), 4),
                        "median": round(float(col_data.median()), 4),
                        "std": round(float(col_data.std()), 4),
                        "min": round(float(col_data.min()), 4),
                        "max": round(float(col_data.max()), 4),
                    },
                }

        return {
            "total_columns_with_outliers": len(outlier_report),
            "details": outlier_report,
        }

    @staticmethod
    def _correlation_analysis(df: pd.DataFrame) -> Dict:
        """Compute and analyze correlations between numerical features."""
        numerical = df.select_dtypes(include=["number"])

        if numerical.shape[1] < 2:
            return {"message": "Insufficient numerical columns for correlation analysis."}

        corr_matrix = numerical.corr().round(4)

        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.5:
                    strong_correlations.append({
                        "feature_1": corr_matrix.columns[i],
                        "feature_2": corr_matrix.columns[j],
                        "correlation": float(val),
                        "strength": (
                            "Strong" if abs(val) > 0.7
                            else "Moderate"
                        ),
                        "direction": "Positive" if val > 0 else "Negative",
                    })

        # Sort by absolute correlation
        strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "top_5": strong_correlations[:5],
        }

    @staticmethod
    def _distribution_analysis(df: pd.DataFrame) -> Dict:
        """Analyze the distribution of numerical and categorical features."""
        results = {"numerical": {}, "categorical": {}}

        # Numerical distributions
        for col in df.select_dtypes(include=["number"]).columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            # Normality test (Shapiro-Wilk for small samples, D'Agostino for large)
            if len(col_data) > 5000:
                sample = col_data.sample(5000, random_state=42)
            else:
                sample = col_data

            try:
                if len(sample) >= 20:
                    stat, p_value = stats.normaltest(sample)
                    is_normal = p_value > 0.05
                else:
                    is_normal = False
                    p_value = 0
            except Exception:
                is_normal = False
                p_value = 0

            results["numerical"][col] = {
                "mean": round(float(col_data.mean()), 4),
                "median": round(float(col_data.median()), 4),
                "std": round(float(col_data.std()), 4),
                "skewness": round(float(col_data.skew()), 4),
                "kurtosis": round(float(col_data.kurtosis()), 4),
                "is_normal": bool(is_normal),
                "normality_p_value": round(float(p_value), 6),
            }

        # Categorical distributions
        for col in df.select_dtypes(include=["object", "category"]).columns:
            value_counts = df[col].value_counts()
            results["categorical"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": safe_json_serialize(value_counts.head(10).to_dict()),
                "entropy": round(float(stats.entropy(value_counts.values)), 4),
            }

        return results

    @staticmethod
    def _feature_importance(df: pd.DataFrame, target_col: str) -> Dict:
        """Calculate feature importance using correlation and mutual information."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder

        if target_col not in df.columns:
            return {"error": f"Target column '{target_col}' not found."}

        # Prepare data
        df_clean = df.dropna()
        if len(df_clean) < 10:
            return {"error": "Insufficient data after removing missing values."}

        # Encode target
        le = LabelEncoder()
        try:
            y = le.fit_transform(df_clean[target_col])
        except Exception:
            return {"error": f"Cannot encode target column '{target_col}'."}

        # Select numerical features
        numerical_features = df_clean.select_dtypes(include=["number"]).columns
        numerical_features = [c for c in numerical_features if c != target_col]

        if len(numerical_features) == 0:
            return {"error": "No numerical features available."}

        X = df_clean[numerical_features].fillna(0)

        # Random Forest importance
        try:
            rf = RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=10, n_jobs=-1
            )
            rf.fit(X, y)
            importance = dict(zip(numerical_features, rf.feature_importances_.round(4)))
        except Exception as e:
            importance = {}

        # Correlation with target
        correlations = {}
        for col in numerical_features:
            try:
                corr = df_clean[col].corr(pd.Series(y, index=df_clean.index))
                correlations[col] = round(float(corr), 4)
            except Exception:
                correlations[col] = 0.0

        # Sort by importance
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )
        sorted_correlations = dict(
            sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        )

        return {
            "rf_importance": sorted_importance,
            "correlation_with_target": sorted_correlations,
            "top_features": list(sorted_importance.keys())[:10],
        }

    @staticmethod
    def _risk_profiling(df: pd.DataFrame, target_col: str) -> Dict:
        """Generate risk profiles based on the target column."""
        if target_col not in df.columns:
            return {"error": "Target column not found."}

        target_values = df[target_col].value_counts()
        total = len(df)

        # Risk distribution
        risk_distribution = {
            str(k): {
                "count": int(v),
                "percentage": round(v / total * 100, 2),
            }
            for k, v in target_values.items()
        }

        # Risk breakdown by features
        numerical_cols = df.select_dtypes(include=["number"]).columns
        numerical_cols = [c for c in numerical_cols if c != target_col]

        risk_by_feature = {}
        for col in numerical_cols[:10]:  # Top 10 features
            try:
                grouped = df.groupby(target_col)[col].agg(["mean", "median", "std"])
                risk_by_feature[col] = safe_json_serialize(grouped.round(4).to_dict())
            except Exception:
                continue

        return {
            "target_distribution": risk_distribution,
            "risk_by_feature": risk_by_feature,
            "risk_ratio": round(
                target_values.min() / target_values.max()
                if target_values.max() > 0 else 0,
                4,
            ),
            "is_imbalanced": (
                target_values.min() / target_values.max() < 0.3
                if target_values.max() > 0 else False
            ),
        }

    @staticmethod
    def _generate_charts(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict:
        """Generate all EDA charts as base64-encoded images."""
        charts = {}

        # 1. Missing values chart
        charts["missing_values"] = EDAService._chart_missing_values(df)

        # 2. Correlation heatmap
        charts["correlation_heatmap"] = EDAService._chart_correlation(df)

        # 3. Distribution plots
        charts["distributions"] = EDAService._chart_distributions(df)

        # 4. Target distribution
        if target_col and target_col in df.columns:
            charts["target_distribution"] = EDAService._chart_target(df, target_col)

        # 5. Box plots for outliers
        charts["box_plots"] = EDAService._chart_box_plots(df)

        # 6. Feature importance chart
        if target_col and target_col in df.columns:
            charts["feature_importance"] = EDAService._chart_feature_importance(df, target_col)

        return charts

    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="#0f172a", edgecolor="none")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    @staticmethod
    def _chart_missing_values(df: pd.DataFrame) -> str:
        """Generate missing values bar chart."""
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=True)

        if missing.empty:
            return ""

        fig, ax = plt.subplots(figsize=(10, max(4, len(missing) * 0.4)))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        bars = ax.barh(range(len(missing)), missing.values, color="#818cf8", edgecolor="#6366f1")
        ax.set_yticks(range(len(missing)))
        ax.set_yticklabels(missing.index, color="white", fontsize=9)
        ax.set_xlabel("Missing Count", color="white", fontsize=10)
        ax.set_title("Missing Values by Column", color="white", fontsize=13, fontweight="bold")
        ax.tick_params(colors="white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.spines["left"].set_color("#334155")

        for bar, val in zip(bars, missing.values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    str(int(val)), va="center", color="white", fontsize=8)

        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _chart_correlation(df: pd.DataFrame) -> str:
        """Generate correlation heatmap."""
        numerical = df.select_dtypes(include=["number"])
        if numerical.shape[1] < 2:
            return ""

        # Limit to top 15 columns
        if numerical.shape[1] > 15:
            numerical = numerical.iloc[:, :15]

        corr = numerical.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        im = ax.imshow(corr.values, cmap="RdYlBu_r", aspect="auto", vmin=-1, vmax=1)
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.yaxis.set_tick_params(color="white")
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", color="white", fontsize=8)
        ax.set_yticklabels(corr.columns, color="white", fontsize=8)
        ax.set_title("Feature Correlation Heatmap", color="white", fontsize=13, fontweight="bold", pad=15)

        # Annotate
        for i in range(len(corr)):
            for j in range(len(corr)):
                val = corr.iloc[i, j]
                color = "white" if abs(val) > 0.5 else "#94a3b8"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color=color, fontsize=7)

        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _chart_distributions(df: pd.DataFrame) -> str:
        """Generate distribution histograms for numerical columns."""
        numerical = df.select_dtypes(include=["number"]).columns[:9]  # Max 9

        if len(numerical) == 0:
            return ""

        n_cols = min(3, len(numerical))
        n_rows = (len(numerical) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 3.5 * n_rows))
        fig.patch.set_facecolor("#0f172a")

        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        for i, col in enumerate(numerical):
            ax = axes[i]
            ax.set_facecolor("#1e293b")
            data = df[col].dropna()

            ax.hist(data, bins=30, color="#818cf8", edgecolor="#6366f1", alpha=0.8)
            ax.set_title(col, color="white", fontsize=10, fontweight="bold")
            ax.tick_params(colors="white", labelsize=7)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_color("#334155")
            ax.spines["left"].set_color("#334155")

        # Hide unused axes
        for j in range(len(numerical), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle("Feature Distributions", color="white", fontsize=13,
                     fontweight="bold", y=1.02)
        fig.tight_layout()

        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _chart_target(df: pd.DataFrame, target_col: str) -> str:
        """Generate target variable distribution chart."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("#0f172a")

        counts = df[target_col].value_counts()
        labels = [str(l) for l in counts.index]
        colors_list = EDAService.COLORS[: len(counts)]

        # Bar chart
        ax = axes[0]
        ax.set_facecolor("#1e293b")
        ax.bar(range(len(counts)), counts.values, color=colors_list, edgecolor="#1e293b")
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(labels, color="white", fontsize=9)
        ax.set_ylabel("Count", color="white")
        ax.set_title("Target Distribution", color="white", fontsize=12, fontweight="bold")
        ax.tick_params(colors="white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.spines["left"].set_color("#334155")

        # Pie chart
        ax2 = axes[1]
        ax2.set_facecolor("#0f172a")
        wedges, texts, autotexts = ax2.pie(
            counts.values, labels=labels, colors=colors_list,
            autopct="%1.1f%%", startangle=140,
            textprops={"color": "white", "fontsize": 9},
        )
        ax2.set_title("Target Proportion", color="white", fontsize=12, fontweight="bold")

        fig.tight_layout()
        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _chart_box_plots(df: pd.DataFrame) -> str:
        """Generate box plots for outlier visualization."""
        numerical = df.select_dtypes(include=["number"]).columns[:9]

        if len(numerical) == 0:
            return ""

        n_cols = min(3, len(numerical))
        n_rows = (len(numerical) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 3.5 * n_rows))
        fig.patch.set_facecolor("#0f172a")

        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        for i, col in enumerate(numerical):
            ax = axes[i]
            ax.set_facecolor("#1e293b")
            data = df[col].dropna()

            bp = ax.boxplot(
                data, patch_artist=True,
                boxprops=dict(facecolor="#818cf8", color="#6366f1"),
                whiskerprops=dict(color="#94a3b8"),
                capprops=dict(color="#94a3b8"),
                medianprops=dict(color="#facc15", linewidth=2),
                flierprops=dict(marker="o", markerfacecolor="#f87171", markersize=4),
            )
            ax.set_title(col, color="white", fontsize=10, fontweight="bold")
            ax.tick_params(colors="white", labelsize=7)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_color("#334155")
            ax.spines["left"].set_color("#334155")

        for j in range(len(numerical), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle("Outlier Detection (Box Plots)", color="white", fontsize=13,
                     fontweight="bold", y=1.02)
        fig.tight_layout()

        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _chart_feature_importance(df: pd.DataFrame, target_col: str) -> str:
        """Generate feature importance chart."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder

        df_clean = df.dropna()
        if len(df_clean) < 10:
            return ""

        le = LabelEncoder()
        try:
            y = le.fit_transform(df_clean[target_col])
        except Exception:
            return ""

        numerical_features = [c for c in df_clean.select_dtypes(include=["number"]).columns
                              if c != target_col]
        if not numerical_features:
            return ""

        X = df_clean[numerical_features].fillna(0)

        try:
            rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            rf.fit(X, y)
            importance = pd.Series(rf.feature_importances_, index=numerical_features)
            importance = importance.sort_values(ascending=True)
        except Exception:
            return ""

        fig, ax = plt.subplots(figsize=(10, max(4, len(importance) * 0.35)))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        bars = ax.barh(range(len(importance)), importance.values,
                       color="#818cf8", edgecolor="#6366f1")
        ax.set_yticks(range(len(importance)))
        ax.set_yticklabels(importance.index, color="white", fontsize=9)
        ax.set_xlabel("Importance", color="white", fontsize=10)
        ax.set_title("Feature Importance (Random Forest)", color="white",
                     fontsize=13, fontweight="bold")
        ax.tick_params(colors="white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.spines["left"].set_color("#334155")

        return EDAService._fig_to_base64(fig)

    @staticmethod
    def _generate_insights(
        df: pd.DataFrame,
        target_col: Optional[str],
        results: Dict,
    ) -> List[str]:
        """Generate automated business insights from the analysis."""
        insights = []

        # Data quality insights
        summary = results.get("summary", {})
        missing = results.get("missing_values", {})
        duplicates = results.get("duplicates", {})

        insights.append(
            f"Dataset contains {summary.get('rows', 0):,} records across "
            f"{summary.get('columns', 0)} features "
            f"({summary.get('column_count', {}).get('numerical', 0)} numerical, "
            f"{summary.get('column_count', {}).get('categorical', 0)} categorical)."
        )

        total_missing = missing.get("total_missing", 0)
        if total_missing > 0:
            pct = total_missing / (summary.get("rows", 1) * summary.get("columns", 1)) * 100
            insights.append(
                f"Data quality alert: {total_missing:,} missing values detected "
                f"({pct:.1f}% of all cells) across "
                f"{missing.get('columns_with_missing', 0)} columns."
            )
        else:
            insights.append("Data quality is excellent — no missing values detected.")

        n_dups = duplicates.get("total_duplicates", 0)
        if n_dups > 0:
            insights.append(
                f"Found {n_dups:,} duplicate records "
                f"({duplicates.get('duplicate_percentage', 0):.1f}%). "
                f"Deduplication recommended before modeling."
            )

        # Outlier insights
        outliers = results.get("outliers", {})
        n_outlier_cols = outliers.get("total_columns_with_outliers", 0)
        if n_outlier_cols > 0:
            insights.append(
                f"{n_outlier_cols} features contain outliers. "
                "Consider capping or transformation before model training."
            )

        # Correlation insights
        corr = results.get("correlation", {})
        strong = corr.get("strong_correlations", [])
        if strong:
            top = strong[0]
            insights.append(
                f"Strongest correlation: {top['feature_1']} ↔ {top['feature_2']} "
                f"(r = {top['correlation']:.3f}, {top['direction']}). "
                f"Consider multicollinearity effects."
            )

        # Risk insights
        risk = results.get("risk_profile", {})
        if risk and "target_distribution" in risk:
            is_imbal = risk.get("is_imbalanced", False)
            if is_imbal:
                insights.append(
                    "⚠️ Target variable is imbalanced. Use SMOTE, class weights, "
                    "or stratified sampling to mitigate bias."
                )

        # Feature importance insights
        fi = results.get("feature_importance", {})
        top_features = fi.get("top_features", [])
        if top_features:
            insights.append(
                f"Top predictive features: {', '.join(top_features[:5])}. "
                "Focus data collection and monitoring on these variables."
            )

        return insights
