"""Price movement predictor using ensemble ML."""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from .preprocessing import FeatureEngineer


class PricePredictor:
    """Ensemble predictor for price direction."""

    def __init__(self):
        self.models = {
            "rf": RandomForestClassifier(n_estimators=100, random_state=42),
            "gb": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "lr": LogisticRegression(max_iter=1000, random_state=42),
        }
        self.engineer = FeatureEngineer()
        self.is_trained = False

    def train(self, df: pd.DataFrame, target_horizon: int = 5) -> Dict[str, float]:
        """Train all models on historical data."""
        X, y, _ = self.engineer.prepare_train_data(df, target_horizon)

        scores = {}
        for name, model in self.models.items():
            model.fit(X, y)
            scores[name] = model.score(X, y)

        self.is_trained = True
        return scores

    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict direction using ensemble vote."""
        if not self.is_trained:
            return {"error": "Model not trained"}

        X = self.engineer.transform(df)
        if len(X) == 0:
            return {"error": "Insufficient data for prediction"}

        latest = X[-1:]
        predictions = {}
        probabilities = {}

        for name, model in self.models.items():
            pred = model.predict(latest)[0]
            proba = model.predict_proba(latest)[0] if hasattr(model, "predict_proba") else np.array([0.33, 0.33, 0.33])
            predictions[name] = int(pred)
            probabilities[name] = proba.tolist()

        # Ensemble vote
        votes = list(predictions.values())
        bullish_votes = sum(1 for v in votes if v == 1)
        bearish_votes = sum(1 for v in votes if v == -1)
        neutral_votes = sum(1 for v in votes if v == 0)

        total = len(votes)
        bullish_prob = bullish_votes / total
        bearish_prob = bearish_votes / total
        neutral_prob = neutral_votes / total

        if bullish_prob > bearish_prob and bullish_prob > neutral_prob:
            prediction = "bullish"
            confidence = bullish_prob
        elif bearish_prob > bullish_prob and bearish_prob > neutral_prob:
            prediction = "bearish"
            confidence = bearish_prob
        else:
            prediction = "neutral"
            confidence = neutral_prob

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "bullish_prob": round(bullish_prob, 4),
            "bearish_prob": round(bearish_prob, 4),
            "neutral_prob": round(neutral_prob, 4),
            "model_votes": predictions,
        }
