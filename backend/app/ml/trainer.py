"""Model training pipeline with cross-validation."""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from .predictor import PricePredictor
from .preprocessing import FeatureEngineer


class ModelTrainer:
    """Training pipeline with time-series cross-validation."""

    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        self.best_model: Optional[PricePredictor] = None
        self.best_score = 0.0

    def cross_validate(
        self,
        df: pd.DataFrame,
        target_horizon: int = 5,
    ) -> Dict[str, Any]:
        """Run time-series cross-validation."""
        engineer = FeatureEngineer()
        X, y, feature_names = engineer.prepare_train_data(df, target_horizon)

        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        scores = []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            predictor = PricePredictor()
            for name, model in predictor.models.items():
                model.fit(X_train, y_train)

            # Evaluate
            correct = 0
            for i in range(len(X_test)):
                latest = X_test[i:i+1]
                votes = []
                for name, model in predictor.models.items():
                    pred = model.predict(latest)[0]
                    votes.append(pred)

                ensemble_pred = max(set(votes), key=votes.count)
                if ensemble_pred == y_test[i]:
                    correct += 1

            accuracy = correct / len(X_test) if len(X_test) > 0 else 0
            scores.append(accuracy)

        return {
            "cv_scores": [round(s, 4) for s in scores],
            "mean_accuracy": round(np.mean(scores), 4),
            "std_accuracy": round(np.std(scores), 4),
            "feature_names": feature_names,
        }

    def train_final(self, df: pd.DataFrame, target_horizon: int = 5) -> PricePredictor:
        """Train final model on all data."""
        predictor = PricePredictor()
        predictor.train(df, target_horizon)
        self.best_model = predictor
        return predictor
