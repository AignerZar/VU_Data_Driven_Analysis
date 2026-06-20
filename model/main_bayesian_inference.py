import arviz as az

from config import DATA_PATH
from data import load_landslide_data, prepare_data
from model import build_and_sample_model, predict_posterior
from evaluation import evaluate_model
from plots import make_all_plots
from utils import save_predictions


def main():
    df = load_landslide_data(DATA_PATH)

    X_train, X_test, y_train, y_test, df_train, df_test, scaler = prepare_data(df)

    model, idata = build_and_sample_model(X_train, y_train)

    print("\nPosterior Summary:")
    print(
        az.summary(
            idata,
            var_names=["alpha", "beta"],
        )
    )

    predictions = predict_posterior(idata, X_test)

    evaluate_model(y_test, predictions)
    save_predictions(df_test, predictions)
    make_all_plots(df, idata, y_test, predictions)


if __name__ == "__main__":
    main()