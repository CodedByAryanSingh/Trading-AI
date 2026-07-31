"""Model prediction utilities.

Provides Predictor class responsible for loading trained models and making
predictions. Supports scikit-learn estimators and xgboost models that
implement predict and predict_proba.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

import os
import joblib
import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


class PredictorError(Exception):
    """Raised when prediction or model IO fails."""


class Predictor:
    """Load a saved model and provide prediction helpers.

    Example:
        p = Predictor.load("models/rf.joblib")
        preds = p.predict(X)
        probs = p.predict_proba(X)
        conf = p.predict_with_confidence(X)
    """

    def __init__(self, model: Any) -> None:
        self.model = model

    @classmethod
    def load(cls, path: str) -> "Predictor":
        """Load a model from disk using joblib.

        Args:
            path: file path to the joblib/pickle file
        Returns:
            Predictor instance wrapping the loaded model
        """
        if not os.path.exists(path):
            raise PredictorError(f"Model file not found: {path}")
        try:
            model = joblib.load(path)
            logger.info("Loaded model from %s", path)
            return cls(model)
        except Exception:
            logger.exception("Failed to load model from %s", path)
            raise PredictorError("Failed to load model")

    def save(self, path: str) -> None:
        """Persist the model to disk using joblib."""
        try:
            dirpath = os.path.dirname(path)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            joblib.dump(self.model, path)
            logger.info("Saved model to %s", path)
        except Exception:
            logger.exception("Failed to save model to %s", path)
            raise PredictorError("Failed to save model")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return class predictions for X."""
        try:
            arr = X.values if isinstance(X, pd.DataFrame) else X
            preds = self.model.predict(arr)
            return np.asarray(preds)
        except Exception:
            logger.exception("Prediction failed")
            raise PredictorError("Prediction failed")

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return predicted class probabilities for X.

        Some estimators may not support predict_proba; in that case this
        method will raise PredictorError.
        """
        try:
            arr = X.values if isinstance(X, pd.DataFrame) else X
            probs = self.model.predict_proba(arr)
            return np.asarray(probs)
        except Exception:
            logger.exception("predict_proba failed")
            raise PredictorError("predict_proba failed")

    def predict_with_confidence(self, X: pd.DataFrame) -> Sequence[dict]:
        """Return predictions with confidence scores.

        Returns a list of dicts: { 'prediction': cls, 'confidence': prob }
        where confidence is the max class probability for the chosen class.
        """
        preds = self.predict(X)
        try:
            probs = self.predict_proba(X)
            confidences = np.max(probs, axis=1)
        except PredictorError:
            # if no probabilities, fallback to 1.0 confidence
            confidences = np.ones(len(preds))
        result = []
        for p, c in zip(preds, confidences):
            result.append({"prediction": p, "confidence": float(c)})
        return result
