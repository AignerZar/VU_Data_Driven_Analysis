"""
File for loading in the input data and also to prepare the data for later use in the model
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from config import FEATURES, TARGET, TEST_SIZE, RANDOM_SEED


def load_landslide_data(path):
    df = pd.read_csv(path)

    required_columns = FEATURES + [TARGET]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column missing: {col}")

    df = df.dropna(subset=required_columns).copy()
    df[TARGET] = df[TARGET].astype(int)

    print("\nDistribution of labels:")
    print(df[TARGET].value_counts())
    print(df[TARGET].value_counts(normalize=True))

    if df[TARGET].nunique() < 2:
        raise ValueError("Not two classes.")

    return df


def prepare_data(df):
    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X,
        y,
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, df_train, df_test, scaler