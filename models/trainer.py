"""Model training utilities.

Provides Trainer class to train tree-based models (RandomForest, XGBoost)
with time-series aware cross-validation. Designed for deterministic,
unit-testable behavior and clear logging.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


class TrainerError(Exception):
    """Raised when training fails."""


class Trainer:
    """Trainer for tree-based classification models.

    This trainer supports RandomForest (scikit-learn) and XGBoost if
    available. It uses TimeSeriesSplit by default for cross validation to
    respect temporal ordering of time series data.
    """

    def __init__(self, random_state: Optional[int] = 42) -> None:
        self.random_state = random_state

    def _build_rf(self, params: Optional[Dict[str, Any]] = None):
        try:
            from sklearn.ensemble import RandomForestClassifier

            params = params or {}
            params.setdefault("n_estimators", 100)
            params.setdefault("random_state", self.random_state)
            model = RandomForestClassifier(**params)
            return model
        except Exception as exc:  # pragma: no cover - import/runtime environment
            logger.exception("Failed to construct RandomForestClassifier: %s", exc)
            raise TrainerError("scikit-learn RandomForestClassifier is required")

    def _build_xgb(self, params: Optional[Dict[str, Any]] = None):
        try:
            import xgboost as xgb  # type: ignore

            params = params or {}
            params.setdefault("n_estimators", 100)
            params.setdefault("random_state", self.random_state)
            model = xgb.XGBClassifier(**params)
            return model
        except Exception as exc:  # pragma: no cover - import/runtime environment
            logger.exception("Failed to construct XGBClassifier: %s", exc)
            raise TrainerError("xgboost is required for XGBoost training")

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model_type: str = "rf",
        params: Optional[Dict[str, Any]] = None,
        cv_splits: int = 5,
        scoring: Optional[str] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        """Train a model and return the fitted estimator and training report.

        Args:
            X: feature matrix (pd.DataFrame)
            y: target series (pd.Series)
            model_type: 'rf' for RandomForest, 'xgb' for XGBoost
            params: model hyperparameters
            cv_splits: number of TimeSeriesSplit folds for evaluation
            scoring: scoring metric for cross_val_score (None defaults to 'roc_auc' for binary)

        Returns:
            (fitted_model, report_dict) where report contains cv_scores and final training info
        """
        if not isinstance(X, (pd.DataFrame, np.ndarray)):
            raise TrainerError("X must be a pandas DataFrame or numpy array")
        if not isinstance(y, (pd.Series, np.ndarray)):
            raise TrainerError("y must be a pandas Series or numpy array")

        X_arr = X.values if isinstance(X, pd.DataFrame) else X
        y_arr = y.values if isinstance(y, pd.Series) else y

        # select scoring default
        if scoring is None:
            unique_classes = np.unique(y_arr)
            if unique_classes.shape[0] == 2:
                scoring = "roc_auc"
            else:
                scoring = "accuracy"

        # build model
        model_type = model_type.lower()
        if model_type == "rf":
            model = self._build_rf(params)
        elif model_type in ("xgb", "xgboost"):
            model = self._build_xgb(params)
        else:
            raise TrainerError(f"Unsupported model_type: {model_type}")

        # cross-validate with TimeSeriesSplit
        try:
            from sklearn.model_selection import TimeSeriesSplit, cross_val_score

            tscv = TimeSeriesSplit(n_splits=cv_splits)
            logger.debug("Starting cross-validation with %s splits and scoring=%s", cv_splits, scoring)
            scores = cross_val_score(model, X_arr, y_arr, cv=tscv, scoring=scoring, n_jobs=-1)
            logger.info("CV scores (%s): %s", scoring, scores)
        except Exception:
            logger.exception("Cross-validation failed; proceeding to fit full data")
            scores = np.array([])

        # fit on full data
        try:
            model.fit(X_arr, y_arr)
        except Exception as exc:
            logger.exception("Model fitting failed: %s", exc)
            raise TrainerError("Model fitting failed")

        report = {
            "model_type": model_type,
            "cv_scoring": scoring,
            "cv_scores": scores.tolist() if hasattr(scores, "tolist") else [],
            "n_samples": int(X_arr.shape[0]),
            "n_features": int(X_arr.shape[1]) if X_arr.ndim > 1 else 1,
        }
        return model, report
