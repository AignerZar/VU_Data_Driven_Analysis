import pandas as pd

from config import PREDICTION_OUTPUT_PATH


def save_predictions(df_test, predictions):
    df_results = df_test.reset_index(drop=True).copy()
    predictions = predictions.reset_index(drop=True)

    df_results = pd.concat([df_results, predictions], axis=1)
    df_results.to_csv(PREDICTION_OUTPUT_PATH, index=False)

    print(f"\nPredictions saved as: {PREDICTION_OUTPUT_PATH}")
    print(df_results.head())