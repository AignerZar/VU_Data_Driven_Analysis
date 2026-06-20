"""
Code for all the evaluation function to later analyze the performance of the model
"""
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from config import THRESHOLD


def evaluate_model(y_test, predictions, threshold=THRESHOLD):
    y_prob = predictions["p_landslide_mean"].values
    y_pred = (y_prob >= threshold).astype(int)

    print("\n==============================")
    print("Model Evaluation")
    print("==============================")

    print(f"Threshold: {threshold}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("ROC AUC:", roc_auc_score(y_test, y_prob))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))