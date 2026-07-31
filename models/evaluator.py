"""Model evaluation utilities.

Provides Evaluator with common classification metrics and helper functions
for computing prediction confidence and calibration summaries.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from utils.logger import get_logger

logger = get_logger(__name__)


class EvaluatorError(Exception):
    """Raised when evaluation fails."""


class Evaluator:
    """Compute classification metrics for predictions.

    Methods are static/stateless so they are easy to unit test.
    """

    @staticmethod
    def classification_report(y_true: Sequence, y_pred: Sequence, y_proba: Optional[Sequence] = None) -> Dict[str, object]:
        """Return a dictionary of common classification metrics.

        Args:
            y_true: ground truth labels
            y_pred: predicted labels
            y_proba: optional predicted probabilities for positive class (for roc_auc)

        Returns:
            dict with keys accuracy, precision, recall, f1, roc_auc (if available), confusion
        """
        try:
            y_true_arr = np.asarray(y_true)
            y_pred_arr = np.asarray(y_pred)
            acc = float(accuracy_score(y_true_arr, y_pred_arr))
            prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
            rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
            f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))
            cm = confusion_matrix(y_true_arr, y_pred_arr).tolist()
            report = {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "confusion_matrix": cm,
            }
            if y_proba is not None:
                try:
                    y_proba_arr = np.asarray(y_proba)
                    # if multi-dim (n_samples, n_classes), take positive class prob
                    if y_proba_arr.ndim == 2:
                        # choose second column as positive by convention
                        if y_proba_arr.shape[1] >= 2:
                            pos = y_proba_arr[:, 1]
                        else:
                            pos = y_proba_arr[:, 0]
                    else:
                        pos = y_proba_arr
                    roc = float(roc_auc_score(y_true_arr, pos))
                    report["roc_auc"] = roc
                except Exception:
                    logger.exception("Failed to compute ROC AUC")
            return report
        except Exception as exc:
            logger.exception("Evaluation failed: %s", exc)
            raise EvaluatorError("Evaluation failed")

    @staticmethod
    def prediction_confidence(y_proba: Sequence) -> Sequence:
        """Return per-sample confidence as max predicted probability.

        Args:
            y_proba: array-like of probabilities (n_samples,) or (n_samples, n_classes)
        Returns:
            numpy array of confidence scores in [0,1]
        """
        arr = np.asarray(y_proba)
        if arr.ndim == 1:
            return arr
        # max across classes
        return np.max(arr, axis=1)
