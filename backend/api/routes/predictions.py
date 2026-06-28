"""
Predictions API Routes
Triggers model training, auto-selection of the best model, and returns performance/explanation metrics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Prediction
from services.dataset_service import DatasetService
from services.ml_service import MLService
from utils.helpers import safe_json_serialize

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.post("/{dataset_id}/train")
def train_models(dataset_id: int, db: Session = Depends(get_db)):
    """
    Train and evaluate Logistic Regression, Decision Tree, and Random Forest models.
    Select the best model automatically.
    """
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not dataset.target_column:
        raise HTTPException(status_code=400, detail="Target column must be set prior to training models.")

    try:
        df = DatasetService.load_dataframe(dataset)
        ml_service = MLService()
        training_results = ml_service.train_and_evaluate(df, dataset.target_column, dataset.id)

        # Clear old predictions for this dataset
        db.query(Prediction).filter(Prediction.dataset_id == dataset_id).delete()

        # Save each model outcome in the database
        best_model_key = training_results["best_model"]
        for key, res in training_results["models"].items():
            is_best = (key == best_model_key)
            db_pred = Prediction(
                dataset_id=dataset_id,
                model_name=res["model_name"],
                accuracy=res["metrics"].get("accuracy"),
                precision=res["metrics"].get("precision"),
                recall=res["metrics"].get("recall"),
                f1_score=res["metrics"].get("f1"),
                roc_auc=res["metrics"].get("roc_auc"),
                confusion_matrix=res["confusion_matrix"],
                feature_importance=res["feature_importance"],
                classification_report=res["classification_report"],
                prediction_probabilities=training_results.get("prediction_probabilities", []) if is_best else [],
                explanations=res["explanations"] if is_best else [],
                is_best_model=is_best,
                parameters=MLService.MODELS[key]["params"]
            )
            db.add(db_pred)

        dataset.status = "predicted"
        db.commit()

        return training_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training pipeline failed: {str(e)}")

@router.get("/{dataset_id}/results")
def get_prediction_results(dataset_id: int, db: Session = Depends(get_db)):
    """Retrieve saved model training results and explanations."""
    predictions = db.query(Prediction).filter(Prediction.dataset_id == dataset_id).all()
    if not predictions:
        raise HTTPException(status_code=404, detail="No training results found for this dataset. Train models first.")

    res_dict = {"models": {}, "best_model": None}
    for p in predictions:
        key_name = next((k for k, v in MLService.MODELS.items() if v["name"] == p.model_name), p.model_name.lower().replace(" ", "_"))
        res_dict["models"][key_name] = {
            "model_name": p.model_name,
            "metrics": {
                "accuracy": p.accuracy,
                "precision": p.precision,
                "recall": p.recall,
                "f1": p.f1_score,
                "roc_auc": p.roc_auc
            },
            "confusion_matrix": p.confusion_matrix,
            "feature_importance": p.feature_importance,
            "classification_report": p.classification_report,
            "explanations": p.explanations,
            "is_best": p.is_best_model
        }
        if p.is_best_model:
            res_dict["best_model"] = key_name
            res_dict["best_model_name"] = p.model_name
            res_dict["prediction_probabilities"] = p.prediction_probabilities
            res_dict["explanations"] = p.explanations

    return safe_json_serialize(res_dict)
