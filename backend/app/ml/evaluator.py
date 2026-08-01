"""Model evaluation and diagnostics."""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from .predictor import PricePredictor
from .preprocessing import FeatureEngineer


class ModelEvaluator:
    """Evaluate trained models on out-of-sample data."""

    def __init__(self, predictor: PricePredictor):
        self.predictor = predictor

    def evaluate(self, df: pd.DataFrame, target_horizon: int = 5) -> Dict[str, Any]:
        """Evaluate model performance."""
        if not self.predictor.is_trained:
            return {"error": "Model not trained"}

        engineer = FeatureEngineer()
        X, y_true, _ = engineer.prepare_train_data(df, target_horizon)

        y_pred = []
        for i in range(len(X)):
            latest = X[i:i+1]
            votes = []
            for name, model in self.predictor.models.items():
                pred = model.predict(latest)[0]
                votes.append(pred)
            ensemble_pred = max(set(votes), key=votes.count)
            y_pred.append(ensemble_pred)

        y_pred = np.array(y_pred)

        return {
            "accuracy": round(accuracy_score(y_true, y_pred), 4),
            "classification_report": classification_report(y_true, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
            "samples": len(y_true),
        }

    def feature_importance(self) -> Dict[str, List[float]]:
        """Extract feature importances from tree-based models."""
        importances = {}

        if hasattr(self.predictor.models.get("rf"), "feature_importances_"):
            importances["rf"] = self.predictor.models["rf"].feature_importances_.tolist()

        if hasattr(self.predictor.models.get("gb"), "feature_importances_"):
            importances["gb"] = self.predictor.models["gb"].feature_importances_.tolist()

        return importances
