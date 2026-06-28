"""
ML Service
Machine Learning prediction engine supporting Logistic Regression,
Decision Tree, and Random Forest. Automatically selects the best model
based on cross-validation and generates explainable predictions.
"""
import io
import base64
import warnings
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve,
)
from sklearn.impute import SimpleImputer
import joblib

from config.settings import settings
from utils.helpers import safe_json_serialize

warnings.filterwarnings("ignore")


class MLService:
    """
    Production ML pipeline for financial risk prediction.
    Supports automatic model selection and explainable predictions.
    """

    MODELS = {
        "logistic_regression": {
            "name": "Logistic Regression",
            "class": LogisticRegression,
            "params": {"max_iter": 1000, "random_state": 42, "class_weight": "balanced"},
        },
        "decision_tree": {
            "name": "Decision Tree",
            "class": DecisionTreeClassifier,
            "params": {"random_state": 42, "max_depth": 10, "class_weight": "balanced"},
        },
        "random_forest": {
            "name": "Random Forest",
            "class": RandomForestClassifier,
            "params": {
                "n_estimators": 100, "random_state": 42,
                "max_depth": 15, "class_weight": "balanced", "n_jobs": -1,
            },
        },
    }

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy="median")
        self.best_model = None
        self.best_model_name = None
        self.feature_names = []

    def train_and_evaluate(
        self,
        df: pd.DataFrame,
        target_col: str,
        dataset_id: int,
    ) -> Dict:
        """
        Train all models, evaluate, select the best, and return results.

        Returns comprehensive results with metrics, charts, and explanations.
        """
        # Prepare data
        X, y, feature_names = self._prepare_data(df, target_col)
        self.feature_names = feature_names

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=settings.TEST_SIZE,
            random_state=settings.RANDOM_STATE,
            stratify=y,
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train and evaluate all models
        all_results = {}
        best_score = -1

        for model_key, model_config in self.MODELS.items():
            model = model_config["class"](**model_config["params"])

            # Train
            model.fit(X_train_scaled, y_train)

            # Predict
            y_pred = model.predict(X_test_scaled)
            y_proba = (
                model.predict_proba(X_test_scaled)
                if hasattr(model, "predict_proba")
                else None
            )

            # Metrics
            metrics = self._compute_metrics(y_test, y_pred, y_proba)

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train_scaled, y_train,
                cv=StratifiedKFold(n_splits=settings.CV_FOLDS, shuffle=True, random_state=42),
                scoring="f1_weighted",
            )
            metrics["cv_mean"] = round(float(cv_scores.mean()), 4)
            metrics["cv_std"] = round(float(cv_scores.std()), 4)

            # Feature importance
            importance = self._get_feature_importance(model, feature_names)

            # Charts
            charts = self._generate_model_charts(
                y_test, y_pred, y_proba, model_config["name"], feature_names, importance
            )

            # Explanations
            explanations = self._generate_explanations(
                model, X_test_scaled, y_pred, y_proba, feature_names,
                num_samples=min(20, len(X_test_scaled)),
            )

            all_results[model_key] = {
                "model_name": model_config["name"],
                "metrics": metrics,
                "feature_importance": importance,
                "charts": charts,
                "explanations": explanations,
                "confusion_matrix": metrics.pop("confusion_matrix_raw", []),
                "classification_report": metrics.pop("classification_report_dict", {}),
            }

            # Track best model
            score = metrics.get("f1", 0)
            if score > best_score:
                best_score = score
                self.best_model = model
                self.best_model_name = model_key

        # Mark best model
        all_results[self.best_model_name]["is_best"] = True

        # Save best model
        model_path = settings.MODELS_DIR / f"best_model_{dataset_id}.joblib"
        joblib.dump({
            "model": self.best_model,
            "scaler": self.scaler,
            "label_encoder": self.label_encoder,
            "imputer": self.imputer,
            "feature_names": feature_names,
        }, model_path)

        # Prediction probabilities for all test samples
        if hasattr(self.best_model, "predict_proba"):
            proba = self.best_model.predict_proba(X_test_scaled)
            prediction_probabilities = [
                {
                    "sample_index": int(i),
                    "predicted_class": int(self.best_model.predict(X_test_scaled[i:i+1])[0]),
                    "probabilities": {
                        str(cls): round(float(p), 4)
                        for cls, p in zip(self.best_model.classes_, proba[i])
                    },
                }
                for i in range(min(50, len(proba)))
            ]
        else:
            prediction_probabilities = []

        return safe_json_serialize({
            "models": all_results,
            "best_model": self.best_model_name,
            "best_model_name": self.MODELS[self.best_model_name]["name"],
            "best_score": best_score,
            "model_path": str(model_path),
            "feature_names": feature_names,
            "prediction_probabilities": prediction_probabilities,
            "dataset_info": {
                "total_samples": len(df),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "features_used": len(feature_names),
            },
        })

    def _prepare_data(
        self, df: pd.DataFrame, target_col: str
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for model training."""
        # Drop rows where target is missing
        df = df.dropna(subset=[target_col])

        # Encode target
        y = self.label_encoder.fit_transform(df[target_col])

        # Select numerical features
        feature_cols = [
            c for c in df.select_dtypes(include=["number"]).columns
            if c != target_col
        ]

        # Also encode useful categorical columns with low cardinality
        for col in df.select_dtypes(include=["object", "category"]).columns:
            if col != target_col and df[col].nunique() <= 10:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
                feature_cols.extend(dummies.columns.tolist())

        X = df[feature_cols].values
        X = self.imputer.fit_transform(X)

        return X, y, feature_cols

    def _compute_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray]
    ) -> Dict:
        """Compute all classification metrics."""
        cm = confusion_matrix(y_true, y_pred)
        cr = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

        metrics = {
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "precision": round(float(precision_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
            "f1": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
            "confusion_matrix_raw": cm.tolist(),
            "classification_report_dict": safe_json_serialize(cr),
        }

        # ROC AUC (handle multiclass)
        if y_proba is not None:
            try:
                if y_proba.shape[1] == 2:
                    metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_proba[:, 1])), 4)
                else:
                    metrics["roc_auc"] = round(float(
                        roc_auc_score(y_true, y_proba, multi_class="ovr", average="weighted")
                    ), 4)
            except Exception:
                metrics["roc_auc"] = 0.0
        else:
            metrics["roc_auc"] = 0.0

        return metrics

    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict:
        """Extract feature importance from trained model."""
        importance = {}

        if hasattr(model, "feature_importances_"):
            # Tree-based models
            for name, imp in zip(feature_names, model.feature_importances_):
                importance[name] = round(float(imp), 6)
        elif hasattr(model, "coef_"):
            # Linear models
            coefs = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
            for name, coef in zip(feature_names, coefs):
                importance[name] = round(float(abs(coef)), 6)

        # Sort descending
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return importance

    def _generate_model_charts(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray],
        model_name: str,
        feature_names: List[str],
        importance: Dict,
    ) -> Dict:
        """Generate model performance charts."""
        charts = {}

        # 1. Confusion Matrix
        charts["confusion_matrix"] = self._chart_confusion_matrix(y_true, y_pred, model_name)

        # 2. ROC Curve
        if y_proba is not None and y_proba.shape[1] == 2:
            charts["roc_curve"] = self._chart_roc_curve(y_true, y_proba[:, 1], model_name)

        # 3. Feature Importance
        if importance:
            charts["feature_importance"] = self._chart_feature_importance(importance, model_name)

        return charts

    def _chart_confusion_matrix(self, y_true, y_pred, model_name) -> str:
        """Generate confusion matrix heatmap."""
        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        im = ax.imshow(cm, cmap="Blues", aspect="auto")
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.yaxis.set_tick_params(color="white")
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

        # Labels
        classes = sorted(set(y_true))
        ax.set_xticks(range(len(classes)))
        ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, color="white")
        ax.set_yticklabels(classes, color="white")
        ax.set_xlabel("Predicted", color="white", fontsize=11)
        ax.set_ylabel("Actual", color="white", fontsize=11)
        ax.set_title(f"Confusion Matrix — {model_name}", color="white",
                     fontsize=13, fontweight="bold")
        ax.tick_params(colors="white")

        # Annotate
        for i in range(len(cm)):
            for j in range(len(cm)):
                color = "white" if cm[i, j] > cm.max() / 2 else "#94a3b8"
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color=color, fontsize=14, fontweight="bold")

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="#0f172a")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _chart_roc_curve(self, y_true, y_score, model_name) -> str:
        """Generate ROC curve chart."""
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc = roc_auc_score(y_true, y_score)

        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        ax.plot(fpr, tpr, color="#818cf8", linewidth=2.5,
                label=f"AUC = {auc:.4f}")
        ax.plot([0, 1], [0, 1], color="#475569", linestyle="--", linewidth=1)
        ax.fill_between(fpr, tpr, alpha=0.15, color="#818cf8")

        ax.set_xlabel("False Positive Rate", color="white", fontsize=11)
        ax.set_ylabel("True Positive Rate", color="white", fontsize=11)
        ax.set_title(f"ROC Curve — {model_name}", color="white",
                     fontsize=13, fontweight="bold")
        ax.legend(loc="lower right", fontsize=10,
                  facecolor="#1e293b", edgecolor="#334155", labelcolor="white")
        ax.tick_params(colors="white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.spines["left"].set_color("#334155")

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="#0f172a")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _chart_feature_importance(self, importance: Dict, model_name: str) -> str:
        """Generate feature importance chart."""
        # Top 15 features
        items = list(importance.items())[:15]
        items.reverse()

        names = [x[0] for x in items]
        values = [x[1] for x in items]

        fig, ax = plt.subplots(figsize=(10, max(4, len(items) * 0.35)))
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#1e293b")

        bars = ax.barh(range(len(names)), values, color="#818cf8", edgecolor="#6366f1")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, color="white", fontsize=9)
        ax.set_xlabel("Importance", color="white", fontsize=10)
        ax.set_title(f"Feature Importance — {model_name}", color="white",
                     fontsize=13, fontweight="bold")
        ax.tick_params(colors="white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("#334155")
        ax.spines["left"].set_color("#334155")

        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="#0f172a")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _generate_explanations(
        self,
        model,
        X_test: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray],
        feature_names: List[str],
        num_samples: int = 10,
    ) -> List[Dict]:
        """
        Generate human-readable explanations for individual predictions.
        Uses feature contribution analysis.
        """
        explanations = []

        for i in range(min(num_samples, len(X_test))):
            sample = X_test[i]
            pred = int(y_pred[i])

            # Feature contributions
            contributions = []
            if hasattr(model, "feature_importances_"):
                for j, name in enumerate(feature_names):
                    contributions.append({
                        "feature": name,
                        "value": round(float(sample[j]), 4),
                        "importance": round(float(model.feature_importances_[j]), 4),
                        "contribution": round(
                            float(sample[j] * model.feature_importances_[j]), 4
                        ),
                    })
            elif hasattr(model, "coef_"):
                coefs = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
                for j, name in enumerate(feature_names):
                    contributions.append({
                        "feature": name,
                        "value": round(float(sample[j]), 4),
                        "coefficient": round(float(coefs[j]), 4),
                        "contribution": round(float(sample[j] * coefs[j]), 4),
                    })

            contributions.sort(key=lambda x: abs(x.get("contribution", 0)), reverse=True)

            explanation = {
                "sample_index": i,
                "predicted_class": pred,
                "confidence": (
                    round(float(y_proba[i].max()), 4)
                    if y_proba is not None
                    else None
                ),
                "top_factors": contributions[:5],
                "narrative": self._build_narrative(pred, contributions[:5]),
            }
            explanations.append(explanation)

        return explanations

    def _build_narrative(self, prediction: int, top_factors: List[Dict]) -> str:
        """Build a human-readable narrative for a prediction."""
        risk_label = "HIGH RISK" if prediction == 1 else "LOW RISK"
        factors_text = []
        for f in top_factors[:3]:
            direction = "high" if f.get("contribution", 0) > 0 else "low"
            factors_text.append(f"{f['feature']} ({direction}: {f['value']:.2f})")

        return (
            f"This customer is classified as {risk_label}. "
            f"Key drivers: {', '.join(factors_text)}. "
            f"These factors had the highest influence on this prediction."
        )

    @staticmethod
    def predict_single(
        model_path: str,
        features: Dict[str, float],
    ) -> Dict:
        """Load a saved model and predict for a single customer."""
        artifacts = joblib.load(model_path)
        model = artifacts["model"]
        scaler = artifacts["scaler"]
        imputer = artifacts["imputer"]
        feature_names = artifacts["feature_names"]

        # Build feature vector
        X = np.array([[features.get(f, 0) for f in feature_names]])
        X = imputer.transform(X)
        X = scaler.transform(X)

        prediction = int(model.predict(X)[0])
        proba = (
            model.predict_proba(X)[0].tolist()
            if hasattr(model, "predict_proba")
            else []
        )

        return {
            "prediction": prediction,
            "risk_label": "HIGH RISK" if prediction == 1 else "LOW RISK",
            "probabilities": proba,
            "features_used": feature_names,
        }
