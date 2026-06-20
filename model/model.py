"""
Defining the bayesian inference model
"""
import numpy as np
import pandas as pd
import pymc as pm

from config import RANDOM_SEED


def build_and_sample_model(X_train, y_train):
    n_features = X_train.shape[1]

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=0, sigma=2)
        beta = pm.Normal("beta", mu=0, sigma=1, shape=n_features)

        logit_p = alpha + pm.math.dot(X_train, beta)

        p_landslide = pm.Deterministic(
            "p_landslide",
            pm.math.sigmoid(logit_p),
        )

        pm.Bernoulli(
            "y_obs",
            p=p_landslide,
            observed=y_train,
        )

        idata = pm.sample(
            draws=3000,
            tune=1000,
            chains=4,
            target_accept=0.9,
            random_seed=RANDOM_SEED,
            return_inferencedata=True,
        )

    return model, idata


def predict_posterior(idata, X_test):
    posterior = idata.posterior.stack(sample=("chain", "draw"))

    alpha = posterior["alpha"].values
    beta = posterior["beta"].values

    mean_probs = []
    lower_95 = []
    upper_95 = []

    for x in X_test:
        logit = alpha + np.dot(beta.T, x)
        prob_samples = 1 / (1 + np.exp(-logit))

        mean_probs.append(np.mean(prob_samples))
        lower_95.append(np.percentile(prob_samples, 2.5))
        upper_95.append(np.percentile(prob_samples, 97.5))

    return pd.DataFrame({
        "p_landslide_mean": mean_probs,
        "p_landslide_lower_95": lower_95,
        "p_landslide_upper_95": upper_95,
    })